from bs4 import BeautifulSoup
import re
import requests
from item import Item
import logging
import config as cfg
logging.basicConfig(filename='imdb_log_file.log',
                    format='%(asctime)s-%(levelname)s-FILE:%(filename)s-FUNC:%(funcName)s-LINE:%(lineno)d-%(message)s',
                    level=logging.INFO)


class ParserException(Exception):
    """
    Created for raising error if page has missing data to parse.
    """
    pass


class Parser:
    """
    Creating objects of parsers
    """

    def __init__(self, contents, name):
        self.contents = contents
        self.name = name

    def parse_contents(self, column_names, omdb_api):
        """
        This functions does the actual parsing on the page, extracting all the relevant data and storing it
        in the imdb list.
        :param column_names:
        :return: list of movies data requested by user
        """

        soup = BeautifulSoup(self.contents, 'lxml')
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

        if len(films) == 0 or not (len(films) == len(crew) == len(imdb_ratings) == len(imdb_num_of_user_ratings)):
            logging.error(f'Invalid page or missing data on page {self.name}')
            raise ParserException(f'Could not parse page {self.name} The data given to the parser is invalid.'
                                  'Please check if there is missing data in the page you are trying to parse.')
        # Verifying there is no missing data from the page we accessed

        else:
            print(f'Successfully parsed IMDb {self.name}, loading data...')
            logging.info(f'Successfully parsed IMDb {self.name}')

        imdb = []

        for i in range(0, len(films)):

            imdb_movie_id = links[i][7:-1]

            # getting each movie container from td class (e.g - 1. The Shawshank Redemption (1994))
            raw_title = films[i].get_text()

            # extracting the movie title only from the movie container
            if 'title' in column_names:
                if self.name == 'movie_meter':
                    title = raw_title[:raw_title.index('(') - 1].strip()
                else:
                    movie_or_ser = (' '.join(raw_title.split()).replace('.', ''))
                    title = movie_or_ser[len(str(i)) + 1:-7]
            else:
                title = None

            # Separating between movies and tv series
            if self.name == 'tv_shows':
                type = 'Series'
            else:
                type = 'Movie'

            # Extracting rating values
            if 'rating' in column_names:
                rating = round(float(imdb_ratings[i]), 2)
            else:
                rating = None

            # extracting the movie/series year only
            if 'year' in column_names:
                year = re.search('\\((.*?)\\)', raw_title).group(1)
            else:
                year = None

            # extracting the rank of the movie/series in the imdb chart
            if 'imdb_chart_rank' in column_names:
                rank = movie_or_ser[:len(str(i)) - (len(movie_or_ser))]
            else:
                rank = None

            # extracting director names
            if 'director' in column_names:
                director = crew[i][0:crew[i].index('(') - 1]
            else:
                director = None

            # extracting the number of votes for each movie
            if 'number_of_votes' in column_names:
                num_votes = "{:,}".format(int(imdb_num_of_user_ratings[i]))
            else:
                num_votes = None


            # extracting actors' names
            if 'main_actors' in column_names:
                main_actors = crew[i][crew[i].index(')') + 3:]
            else:
                main_actors = None

            # Parsing additional information from OMDb API:
            """
            params = {
                'i': imdb_movie_id,
                'type': 'movie',
                'plot': 'full'

            }
            """
            response = omdb_api.query(imdb_movie_id)
            print(response)
            language = response['Language']
            country = response['Country']
            awards = response['Awards']
            duration = response['Runtime']
            writer = response['Writer']
            if self.name != 'tv_shows':
                box_office = response['BoxOffice']
            else:
                box_office = 'N/A'
            if self.name != 'tv_shows':
                production = response['Production']
            else:

                production = 'N/A'
            metascore = response['Metascore']
            genre = response['Genre']
            logging.info('Successfully parsed OMDb API')

            # Creating an object for each movie/series
            item = Item(
                type=type,
                imdb_chart_rank=rank,
                title=title,
                year=year,
                rating=rating,
                director=director,
                number_of_votes=num_votes,
                main_actors=main_actors,
                imdb_movie_id=imdb_movie_id,
                language=language,
                country=country,
                awards=awards,
                duration=duration,
                writer=writer,
                box_office=box_office,
                omdb_metascore=metascore,
                production=production,
                genre=genre)

            imdb.append(item)
            logging.info('Successfully extracted data of columns requested')
        return imdb