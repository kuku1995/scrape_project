from downloader import Downloader
# from parser import Parser
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
import numpy as np

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

    def parse_contents(self, column_names):
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

            raw_title = films[i].get_text()
            # getting each movie container from td class (e.g - 1. The Shawshank Redemption (1994))

            if self.name == 'movie_meter':
                title = raw_title[:raw_title.index('(') - 1].strip()
            else:
                raw_title = (' '.join(raw_title.split()).replace('.', ''))
                if 'movie_title' in column_names:
                    title = raw_title[len(str(i)) + 1:-7]
                # extracting the movie title only from the movie container
                else:
                    title = None

            if self.name == 'tv_shows':
                type = 'Series'
            else:
                type = 'Movie'

            if 'rating' in column_names:
                rating = round(float(imdb_ratings[i]), 2)
            else:
                rating = None
            # extracting ratings values

            if 'year' in column_names:
                year = re.search('\\((.*?)\\)', raw_title).group(1)
            # extracting the movie year only
            else:
                year = None

            if 'imdb_chart_rank' in column_names:
                rank = raw_title[:len(str(i)) - (len(raw_title))]
            # extracting the rank of the movie in the imdb chart
            else:
                rank = None

            if self.name != 'tv_shows':
                if 'director' in column_names:
                    director = crew[i][0:crew[i].index('(') - 1]
                else:
                    director = None
            else:
                director = None
            # extracting director names

            if 'number_of_votes' in column_names:
                num_votes = "{:,}".format(int(imdb_num_of_user_ratings[i]))
            else:
                num_votes = None
            # extracting the number of votes for each movie

            if self.name != 'tv_shows':
                if 'main_actors' in column_names:
                    main_actors = crew[i][crew[i].index(')') + 3:]
                else:
                    main_actors = None
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
            logging.info('Successfully parsed OMDb API')

            # Creating an object for each movie
            item = Item(
                type=type,
                imdb_chart_rank=rank,
                title=title,
                year=year,
                rating=rating,
                director=director,
                number_of_votes=num_votes,
                main_actors=main_actors,
                imdb_movie_id=imdb_movie_id)

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

    # Creating separate downloader objects to access each page
    downloader_top_chart = Downloader()
    downloader_movie_meter = Downloader()
    downloader_tv_shows = Downloader()

    # and accessing each page
    contents_top_chart = downloader_top_chart.download(cfg._TOP_CHART)
    contents_movie_meter = downloader_movie_meter.download(cfg._MOVIE_METER)
    contents_tv_shows = downloader_tv_shows.download(cfg._TOP_TV)

    # creating parser objects for each page
    parser_top_chart = Parser(contents_top_chart, 'top_chart')
    parser_movie_meter = Parser(contents_movie_meter, 'movie_meter')
    parser_tv_shows = Parser(contents_tv_shows, 'tv_shows')


    # Parsing contents from both pages and extracting matching content from API
    data_top_chart = parser_top_chart.parse_contents(column_names)
    data_movie_meter = parser_movie_meter.parse_contents(column_names)
    data_tv_shows = parser_tv_shows.parse_contents(column_names)

    data = data_top_chart + data_movie_meter + data_tv_shows

    for row in data:
        print(row.format(column_names))
    logging.info('Requested data successfully presented to user std output')

    # connect to the database
    con = pymysql.connect(user=cfg.USERNAME, password=cfg.PASSWORD, host=cfg.HOST, db=cfg.DATABASE,
                          client_flag=CLIENT.MULTI_STATEMENTS,
                          cursorclass=pymysql.cursors.DictCursor)

    movies_tb_insert_list = []
    ratings_tb_insert_list = []
    # to_person_table = []
    for movie in data:
        s = " -"
        title = movie.title
        #if movie.duration != 'N/A':
            #duration = int(movie.duration[:3])
        # else:
        #     pass
        type = movie.type
        year = movie.year
        # language = movie.language
        # #language = s.join(movie.language)
        # awards = movie.awards
        # box_office = movie.box_office
        # country = s.join(movie.country)
        # production = movie.production

        imdb_chart_rank = movie.imdb_chart_rank
        rating = movie.rating
        number_of_votes = movie.number_of_votes
        #omdb_metascore = str(movie.omdb_metascore)

        director = movie.director
        if movie.main_actors is not None:
            main_actors = movie.main_actors.split(',')

        movies_tb_insert_list.append((title, type, year))
        ratings_tb_insert_list.append((imdb_chart_rank, rating, number_of_votes))
        # to_person_table.append(main_actors)

    movies_tb_insert_statement = "INSERT INTO Movies&TV (name, type, year_released) VALUES (%s, %s, %s);"
    ratings_tb_insert_statement = "INSERT INTO Ratings (imdb_chart_rank, imdb_rating, num_of_votes) VALUES (%s, %s, %s);"
    # person_tb_insert_statement = "INSERT INTO Person (name) VALUES (%s);"

    cur = con.cursor()
    try:
        cur.executemany(movies_tb_insert_statement, movies_tb_insert_list)
        cur.executemany(ratings_tb_insert_statement, ratings_tb_insert_list)
        # cur.executemany(person_table_insert_statement, to_person_table)
        con.commit()
    except pymysql.err.IntegrityError:
        logging.error(f'Duplicate entries given to DB')
        print("Did not add duplicated values to DB")
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
                        choices=["imdb_chart_rank", "type", "title", "year", "rating", "number_of_votes", "director",
                                 "main_actors", "language", "country", "awards", "duration",
                                 "writer", "box_office", "omdb_metascore", "production", "genre", "all"],
                        required=True)
    args = parser.parse_args()
    if 'all' in args.column_name:
        c = ["imdb_chart_rank", "type", "title", "year", "rating", "number_of_votes", "director",
             "main_actors", "language", "country", "awards", "duration",
             "writer", "box_office", "omdb_metascore", "production", "genre"]
    else:
        c = args.column_name
    scraper(c)


if __name__ == '__main__':
    main()
