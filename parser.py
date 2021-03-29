from bs4 import Beautifulsoup
import re
from item import Item
import logging
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
    def __init__(self, contents):
        self.contents = contents

    def parse_contents(self, column_names):
        """
        This functions does the actual parsing on the page, extracting all the relevant data and storing it
        in the imdb list.
        :param column_names:
        :return: list of movies data requested by user
        """

        soup = Beautifulsoup(self.contents, 'lxml')
        # Using beautiful soup and lxml parrser to parse the data from website.

        films = soup.select('td.titleColumn')
        # <td class="titleColumn"> selects td class to access each container of movies in the list
        # contains film name, year it was released and actors.

        # links = [link.attrs.get('href') for link in soup.select('td.titleColumn a')]
        # gets the specific IMDB URL's for each movie in the chart

        crew = [c.attrs.get('title') for c in soup.select('td.titleColumn a')]
        # gets the starring actors who acted in a particular movie

        imdb_ratings = [rating.attrs.get('data-value') for rating in soup.select('td.posterColumn span[name=ir]')]
        # gets the IMDB rating for each movie

        imdb_num_of_user_ratings = [vote.attrs.get('data-value') for vote in
                                    soup.select('td.posterColumn span[name=nv]')]
        # The number of users which have given a rating to a particular movie

        if len(films) == 0 or not(len(films) == len(crew) == len(imdb_ratings) == len(imdb_num_of_user_ratings)):
            logging.error("Invalid page or missing data on page")
            raise ParserException("Could not parse page. The data given to the parser is invalid."
                                  "Please check if there is missing data in the page you are trying to parse.")
        # Verifying there is no missing data from the page we accessed

        else:
            print('Successfully parsed website')
            logging.info('Successfully parsed website')

        # Tried scraping each movie url as well
        # movies_length = []
        # for link in links:
        #     link = 'https://www.imdb.com/'+link
        #     access = requests.get(link)
        #     soup = Beautifulsoup(access.text, 'lxml')
        #     length = [l.attrs.get('datetime') for l in soup.select('div.subtext time')]
        #     length_of_movie = length[0][2:]
        #     movies_length.append(length_of_movie)

        imdb = []

        for i in range(0, len(films)):

            raw_movie_title = films[i].get_text()
            # getting each movie container from td class (e.g - 1. The Shawshank Redemption (1994))

            movie = (' '.join(raw_movie_title.split()).replace('.', ''))
            if 'movie_title' in column_names:
                title = movie[len(str(i)) + 1:-7]
                # extracting the movie title only from the movie container
            else:
                title = None

            if 'rating' in column_names:
                rating = round(float(imdb_ratings[i]), 2)
            else:
                rating = None

            if 'year' in column_names:
                year = re.search('\\((.*?)\\)', raw_movie_title).group(1)
                # extracting the movie year only
            else:
                year = None

            if 'imdb_chart_rank' in column_names:
                rank = movie[:len(str(i)) - (len(movie))]
                # extracting the rank of the movie in the imdb chart
            else:
                rank = None

            if 'director' in column_names:
                director = crew[i][0:crew[i].index('(') - 1]
            else:
                director = None

            if 'number_of_votes' in column_names:
                num_votes = "{:,}".format(int(imdb_num_of_user_ratings[i]))
            else:
                num_votes = None

            if 'main_actors' in column_names:
                main_actors = crew[i][crew[i].index(')') + 3:]
            else:
                main_actors = None

            # link = 'https://www.imdb.com/' + links[i]
            # access = requests.get(link)
            # soup = Beautifulsoup(access.text, 'lxml')
            # length = soup.select('div.subtext time')
            item = Item(
                imdb_chart_rank=rank,
                movie_title=title,
                year=year,
                rating=rating,
                director=director,
                number_of_votes=num_votes,
                main_actors=main_actors)

            imdb.append(item)
            logging.info('Successfully extracted data from columns requested')
        return imdb


