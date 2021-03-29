from downloader import Downloader
from parser import Parser
import logging
import argparse
import pymysql.cursors
from pymysql.constants import CLIENT

logging.basicConfig(filename='imdb_log_file.log',
                    format='%(asctime)s-%(levelname)s-FILE:%(filename)s-FUNC:%(funcName)s-LINE:%(lineno)d-%(message)s',
                    level=logging.INFO)

_WEBSITE = 'http://www.imdb.com/chart/top'


def scraper(column_names):
    """
    This function creates a Downloader class object, which gets access to IMDb, parses
    the site's content and prints the requested columns by the user to std output.
    :param column_names: IMDb columns requests by user
    :return: Movies data requests by user
    """

    downloader = Downloader()

    contents = downloader.download(_WEBSITE)

    parser = Parser(contents)
    data = parser.parse_contents(column_names)
    for row in data:
        print(row.format(column_names))
    logging.info('Requested data successfully presented to user')

    # Connect to the database
    username = 'root'
    password = 'root'
    host = 'localhost'
    con = pymysql.connect(host=host, user=username, password=password, db='IMDBScrape',
                          client_flag=CLIENT.MULTI_STATEMENTS,
                          cursorclass=pymysql.cursors.DictCursor)

    to_movies_table = []
    to_ratings_table = []
    # to_person_table = []
    for movie in data:
        imdb_chart_rank = movie.imdb_chart_rank
        movie_title = movie.movie_title
        year = movie.year
        rating = movie.rating
        director = movie.director
        number_of_votes = movie.number_of_votes
        main_actors = movie.main_actors.split(',')

        to_movies_table.append((movie_title, year))
        to_ratings_table.append((rating, number_of_votes))
        # to_person_table.append(main_actors)

    movies_table_insert_statement = "INSERT INTO Movies (name, rel_date) VALUES (%s, %s);"
    ratings_table_insert_statement = "INSERT INTO Ratings (no_of_stars, no_of_votes) VALUES (%s, %s);"
    # person_table_insert_statement = "INSERT INTO Person (name) VALUES (%s);"  (this
    # part not ready yet)

    cur = con.cursor()
    cur.executemany(movies_table_insert_statement, to_movies_table)
    cur.executemany(ratings_table_insert_statement, to_ratings_table)
    # cur.executemany(person_table_insert_statement, to_person_table)
    # con.commit()


def main():
    """
    Main function of the module. Parses the different arguments given by command line.
    Executes the scraper function with the arguments give
    """
    parser = argparse.ArgumentParser(prog='IMDb_Scraper', description='Query the IMDb site')
    parser.add_argument("-c", "--column_name", nargs='+', help='Column Names',
                        choices=["imdb_chart_rank", "movie_title", "year", "rating", "number_of_votes", "director",
                                 "main_actors"], required=True)
    args = parser.parse_args()
    scraper(args.column_name)


if __name__ == '__main__':
    main()
