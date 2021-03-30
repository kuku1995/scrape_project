from downloader import Downloader
from parser import Parser
import logging
import argparse
import pymysql.cursors
from pymysql.constants import CLIENT
import config as cfg


logging.basicConfig(filename='imdb_log_file.log',
                    format='%(asctime)s-%(levelname)s-FILE:%(filename)s-FUNC:%(funcName)s-LINE:%(lineno)d-%(message)s',
                    level=logging.INFO)


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
    data = parser.parse_contents(column_names)
    for row in data:
        print(row.format(column_names))
    logging.info('Requested data successfully presented to user')

    # connect to the database
    con = pymysql.connect(user=cfg.USERNAME, password=cfg.PASSWORD, host=cfg.HOST, db='IMDBScrape',
                          client_flag=CLIENT.MULTI_STATEMENTS,
                          cursorclass=pymysql.cursors.DictCursor)

    movies_tb_insert_list = []
    ratings_tb_insert_list = []
    # to_person_table = []
    for movie in data:
        title = movie.movie_title
        duration = int(movie.duration[:3])
        year = movie.year
        country = movie.country
        language = movie.language
        awards = movie.awards
        box_office = movie.box_office
        production = movie.production

        imdb_chart_rank = movie.imdb_chart_rank
        rating = movie.rating
        number_of_votes = movie.number_of_votes
        # omdb_metascore = movie.omdb_metascore

        director = movie.director

        if movie.main_actors is not None:
            main_actors = movie.main_actors.split(',')

        movies_tb_insert_list.append((title, duration, year, awards, box_office))
        ratings_tb_insert_list.append((imdb_chart_rank, rating, number_of_votes))
        # to_person_table.append(main_actors)

    movies_tb_insert_statement = "INSERT INTO Movies (name, duration, year_released, awards, box_office) VALUES (%s, %s, %s, %s, %s);"
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
                                 "writer", "box_office", "omdb_metascore", "production", "genre"],
                        required=True)
    args = parser.parse_args()
    scraper(args.column_name)


if __name__ == '__main__':
    main()
