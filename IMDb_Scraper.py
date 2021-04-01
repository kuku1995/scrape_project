from downloader import Downloader
#from parser import Parser
import logging
import argparse
import pymysql.cursors
from pymysql.constants import CLIENT
import config as cfg
from API import ApiQuery
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

    def __init__(self, contents):
        self.contents = contents

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
        # contains film name, year it was released and actors.

        links = [link.attrs.get('href') for link in soup.select('td.titleColumn a')]
        # gets the specific IMDB URL's for each movie in the chart

        crew = [c.attrs.get('title') for c in soup.select('td.titleColumn a')]
        # gets the starring actors who acted in a particular movie

        imdb_ratings = [rating.attrs.get('data-value') for rating in soup.select('td.posterColumn span[name=ir]')]
        # gets the IMDB rating for each movie

        imdb_num_of_user_ratings = [vote.attrs.get('data-value') for vote in
                                    soup.select('td.posterColumn span[name=nv]')]
        # The number of users which have given a rating to a particular movie

        if len(films) == 0 or not (len(films) == len(crew) == len(imdb_ratings) == len(imdb_num_of_user_ratings)):
            logging.error("Invalid page or missing data on page")
            raise ParserException("Could not parse page. The data given to the parser is invalid."
                                  "Please check if there is missing data in the page you are trying to parse.")
        # Verifying there is no missing data from the page we accessed

        else:
            print('Successfully parsed IMDb')
            logging.info('Successfully parsed IMDb')

        imdb = []

        for i in range(0, len(films)):

            imdb_movie_id = links[i][7:-1]

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
            # extracting ratings values

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
            # extracting director names

            if 'number_of_votes' in column_names:
                num_votes = "{:,}".format(int(imdb_num_of_user_ratings[i]))
            else:
                num_votes = None
            # extracting the number of votes for each movie

            if 'main_actors' in column_names:
                main_actors = crew[i][crew[i].index(')') + 3:]
            else:
                main_actors = None
            # extracting actors' names

            # Parsing additional information from OMDb API:
            """
            params = {
                'i': imdb_movie_id,
                'type': 'movie',
                'plot': 'full'

            }
              """
            response = omdb_api.query(imdb_movie_id)
            # response = requests.get(cfg.API_DATA_URL, params=params).json()
            language = response['Language']
            country = response['Country']
            awards = response['Awards']
            duration = response['Runtime']
            writer = response['Writer']
            box_office = response['BoxOffice']
            metascore = response['Metascore']
            production = response['Production']
            genre = response['Genre']
            logging.info('Successfully parsed OMDb API')

            # Creating an object for each movie
            item = Item(
                imdb_chart_rank=rank,
                movie_title=title,
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


def scraper(column_names):
    """
    This function creates a Downloader class object, which gets access to IMDb, parses
    the site's content and prints the requested columns by the user to std output.
    :param column_names: IMDb columns requests by user
    :return: Movies data requests by user
    """

    downloader = Downloader()

    contents = downloader.download(cfg._WEBSITE)

    parser = Parser(contents)
    api = ApiQuery()
    data = parser.parse_contents(column_names, api)

    for row in data:
        print(row.format(column_names))
    logging.info('Requested data successfully presented to user')

    # connect to the database
    con = pymysql.connect(user=cfg.USERNAME, password=cfg.PASSWORD, host=cfg.HOST, db='IMDBScrape20',
                          client_flag=CLIENT.MULTI_STATEMENTS,
                          cursorclass=pymysql.cursors.DictCursor)

    movies_tb_insert_list = []
    ratings_tb_insert_list = []
    # to_person_table = []
    for movie in data:
        s = "-"
        p = " &"
        title = movie.movie_title
        duration = int(movie.duration[:3])
        year = movie.year
        language = s.join(movie.language)
        awards = movie.awards
        box_office = movie.box_office
        production = p.join(movie.production)

        imdb_chart_rank = movie.imdb_chart_rank
        rating = movie.rating
        number_of_votes = movie.number_of_votes
        omdb_metascore = str(movie.omdb_metascore)
        country = s.join(movie.country)

        director = movie.director
        if movie.main_actors is not None:
            main_actors = movie.main_actors.split(',')

        movies_tb_insert_list.append((title, duration, year, awards, box_office, country, language, production))
        ratings_tb_insert_list.append((imdb_chart_rank, rating, number_of_votes, omdb_metascore ))
        # to_person_table.append(main_actors)

    movies_tb_insert_statement = "INSERT INTO Movies (name, duration, year_released, awards, box_office, country, language, production) VALUES (%s, %s, %s, %s, %s, %s, %s, %s);"
    ratings_tb_insert_statement = "INSERT INTO Ratings (imdb_chart_rank, imdb_rating, num_of_votes, omdb_metascore ) VALUES (%s, %s, %s, %s);"
    # person_tb_insert_statement = "INSERT INTO Person (name) VALUES (%s);"

    cur = con.cursor()
    try:
        cur.executemany(movies_tb_insert_statement, movies_tb_insert_list)
        cur.executemany(ratings_tb_insert_statement, ratings_tb_insert_list)
        # cur.executemany(person_table_insert_statement, to_person_table)
        con.commit()
    except pymysql.err.IntegrityError:
        logging.error(f'Duplicate entries given to DB')
        raise Exception("Did not add duplicated values to DB")
    else:
        print('Data successfully added to IMDbScrape DB')
        logging.info('Data successfully added to IMDBScrape DB')


def main():
    """
    Main function of the module. Parses the different arguments given by command line.
    Executes the scraper function with the arguments give
    """
    parser = argparse.ArgumentParser(prog='IMDb_Scraper', description='Query the IMDb site')
    parser.add_argument("-c", "--column_name", nargs='+', help='Column Names',
                        choices=["imdb_chart_rank", "movie_title", "year", "rating", "number_of_votes", "director",
                                 "main_actors", "language", "country", "awards", "duration",
                                 "writer", "box_office", "omdb_metascore", "production", "genre", "all"],
                        required=True)
    args = parser.parse_args()
    if 'all' in args.column_name:
        c = ["imdb_chart_rank", "movie_title", "year", "rating", "number_of_votes", "director",
                                 "main_actors", "language", "country", "awards", "duration",
                                 "writer", "box_office", "omdb_metascore", "production", "genre"]
    else:
        c = args.column_name
    scraper(c)


if __name__ == '__main__':
    main()
