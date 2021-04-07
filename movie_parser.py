from bs4 import BeautifulSoup
import re
from movies_tv_objects import Item
import logging
import config as cfg


class ParserException(Exception):
    """
    Created for raising error if page has missing data to parse.
    """
    pass


class Parser:
    """
    Creating objects of parsers
    """

    def __init__(self, response, name):
        self.response = response
        self.name = name

    def validate_integrity(self, films, crew, imdb_ratings, imdb_num_of_user_ratings):
        """
        Validating there is no missing data in our containers
        """
        if len(films) == 0 or not (len(films) == len(crew) == len(imdb_ratings) == len(imdb_num_of_user_ratings)):
            logging.error(f'Invalid page or missing data on page {self.name}')
            raise ParserException(f'Could not parse page {self.name} The data given to the parser is invalid.'
                                  'Please check if there is missing data in the page you are trying to parse.')
            # Verifying there is no missing data from the page we accessed

        else:
            logging.info(f'Successfully parsed IMDb {self.name}, loading data...')

    def get_data_containers(self, logger, chart):
        """
        This functions does the actual parsing on the page, extracting all the relevant data and storing it
        in the data list.
        :param logger: for logging
        :param chart: chart name
        :return: data containers
        """
        try:

            soup = BeautifulSoup(self.response, 'lxml')
            # Using beautiful soup and lxml parser to parse the data from website.

            films = soup.select('td.titleColumn')
            # <td class="titleColumn"> selects td class to access each container of movies in the list
            # contains film/series name, year it was released and actors.

            links = [link.attrs.get('href') for link in soup.select('td.titleColumn a')]
            # gets the specific IMDB URL's for each movie/series in the chart

            crew = [c.attrs.get('title') for c in soup.select('td.titleColumn a')]
            # gets the starring actors who acted in a particular movie/series

            imdb_ratings = [rating.attrs.get('data-value') for rating in soup.select('td.posterColumn span[name=ir]')]
            # gets the IMDB rating for each movie/series

            imdb_num_of_user_ratings = [vote.attrs.get('data-value') for vote in
                                        soup.select('td.posterColumn span[name=nv]')]

            # The number of users which have given a rating to a particular movie/series

        except IOError:
            logger.critical(f"Error with page {chart}, unable to extract movie pages id's")
            raise ParserException(f"Error with page {chart}, unable to extract movie pages id's")
        try:
            self.validate_integrity(films, crew, imdb_ratings, imdb_num_of_user_ratings)
        except IOError:
            logger.critical(f"Error with page's data, unable to extract movie pages id's")
            raise ParserException(f"Error with page's data, unable to extract movie pages id's")

        return [films, links, crew, imdb_ratings, imdb_num_of_user_ratings]

    def parse_data(self, container, column_names, omdb_api, chart, logger, stdout_file):
        """
        Parsing the data containers, structuring each movie's data into an item/row for database and printing to user.
        return: list of movies data and lists prepared for database insertion
        """

        films = container[cfg.FILMS]
        links = container[cfg.LINKS]
        crew = container[cfg.CREW]
        imdb_ratings = container[cfg.IMDB_RATING]
        imdb_num_of_user_ratings = container[cfg.IMDB_NUM_OF_USER_RATING]

        data = []
        movies_tb_insert_list = []
        ratings_tb_insert_list = []
        person_tb_insert_list = []
        person_role_tb_insert_list = []

        logger.info(f"Began parsing data from IMDb and OMDb API")
        try:
            for i in range(len(films)):

                imdb_movie_id = links[i][7:-1]

                raw_title = films[i].get_text()

                movie_or_ser = ''
                if self.name == 'MOVIE_METER':
                    title = raw_title[:raw_title.index('(') - 1].strip()
                else:
                    movie_or_ser = (' '.join(raw_title.split()).replace('.', ''))
                    title = movie_or_ser[len(str(i)) + 1:-7]

                if self.name == 'TV_SHOWS':
                    category = 'Series'
                else:
                    category = 'Movie'

                rating = round(float(imdb_ratings[i]), 2)

                year = re.search('\\((.*?)\\)', raw_title).group(1)

                if self.name != 'MOVIE_METER':
                    chart_rank = int(movie_or_ser[:len(str(i)) - (len(movie_or_ser))])
                else:
                    chart_rank = None

                if self.name != 'TV_SHOWS':
                    director = crew[i][0:crew[i].index('(') - 1]
                else:
                    director = None

                num_votes = "{:,}".format(int(imdb_num_of_user_ratings[i]))

                if self.name != 'TV_SHOWS':
                    main_actors = crew[i][crew[i].index(')') + 3:].split(',')
                else:
                    main_actors = crew[i]

                # Parsing additional information from OMDb API:
                """
                params = {
                    'i': imdb_movie_id,
                    'type': 'movie',
                    'plot': 'full'
                }
                """
                response = omdb_api.query(imdb_movie_id)
                language = response['Language']
                country = response['Country']
                awards = response['Awards']
                duration = response['Runtime']

                if duration != 'N/A':
                    duration = int(duration[:3])
                else:
                    duration = None

                writer = response['Writer']

                if writer != 'N/A':
                    if ',' in writer:
                        writer = writer.split(',')[0]
                        if '(' in writer:
                            writer = writer[:writer.index('(') - 1]
                    else:
                        if '(' in writer:
                            writer = writer[:writer.index('(') - 1]
                else:
                    writer = None
                if self.name != 'TV_SHOWS':
                    if response['BoxOffice'] != 'N/A':
                        box_office = int(response['BoxOffice'][1:].replace(',', ''))
                    else:
                        box_office = None
                else:
                    box_office = None
                if self.name != 'TV_SHOWS':
                    production = response['Production']
                else:
                    production = None
                metascore = str(response['Metascore'])
                genre = response['Genre']

                # Creating an object for each movie/series
                item = Item(category=category, imdb_chart_rank=chart_rank, title=title, year=year, rating=rating,
                            director=director, number_of_votes=num_votes, main_actors=main_actors,
                            imdb_movie_id=imdb_movie_id, language=language, country=country, awards=awards,
                            duration=duration, writer=writer, box_office=box_office, omdb_metascore=metascore,
                            production=production, genre=genre, chart=chart)

                print(item.format(column_names))
                std_log = item.format(column_names)
                stdout_file.write(std_log)

                data.append(item)

                movies_tb_insert_list.append((title, category, chart, duration, year, language, awards, box_office,
                                              country, production))
                ratings_tb_insert_list.append((chart_rank, rating, num_votes, metascore))
                person_tb_insert_list.append(director)
                person_role_tb_insert_list.append('director')
                if ',' in main_actors:
                    for actor in main_actors.split(','):
                        person_tb_insert_list.append(actor.strip())
                        person_role_tb_insert_list.append('actor')

                person_tb_insert_list.append(writer)
                person_role_tb_insert_list.append('writer')

            logger.info(f'Successfully extracted all data from IMDb and OMDb API for {chart}')
        except IOError:
            logger.critical(f'Error, unable to extract all data from IMDB and OMDb API.')
            raise ParserException(f'Error, unable to extract all data from IMDB and OMDb API.')

        return data, movies_tb_insert_list, ratings_tb_insert_list, person_tb_insert_list, person_role_tb_insert_list
