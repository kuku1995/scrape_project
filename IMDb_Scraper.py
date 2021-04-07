from downloader import Downloader
from movie_parser import Parser
import argparse
import pymysql
from pymysql.constants import CLIENT
from OMDb_API import ApiQuery
import time
import logging
import config as cfg
import sys


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s-FILE:%(filename)s-FUNC:%(funcName)s-LINE:%(lineno)d-%(message)s')

log_file = logging.FileHandler('imdb_scrape.log')
log_file.setLevel(logging.DEBUG)
log_file.setFormatter(formatter)
logger.addHandler(log_file)

stdout_log = logging.StreamHandler(sys.stdout)
stdout_log.setLevel(logging.INFO)
stdout_log.setFormatter(formatter)
logger.addHandler(stdout_log)


def scraper(column_names, stdout_file):
    """
    This function creates a downloader, parser, api and container for each chart
    and eventually inserts the dara into the IMDb database.
    """

    charts = [cfg._TOP_MOVIE_CHART, cfg._MOVIE_METER, cfg._TV_SHOWS]
    names = ['TOP_MOVIE_CHART', 'MOVIE_METER', 'TV_SHOWS']

    logging.info("Created logger for IMDb scraper")
    for index, chart in enumerate(charts):
        chart_start_time = time.perf_counter()
        downloader = Downloader()
        response = downloader.download(chart, logger)
        parser = Parser(response, names[index])
        api = ApiQuery(f'api_{names[index]}', chart)
        container = parser.get_data_containers(chart, logger)
        data, movies_tb_insert_list, ratings_tb_insert_list, person_tb_insert_list, person_role_tb_insert_list = \
            parser.parse_data(container, column_names, api, chart, logger, stdout_file)

        """
        Before every insert query to the database, make another query to pull all records and scan if they have the record
        they want to insert, and if not then make the insert query
        add the data only if it not in the db already.
        """
        con = pymysql.connect(user=cfg.USERNAME, password=cfg.PASSWORD, host=cfg.HOST, db=cfg.DATABASE,
                               client_flag=CLIENT.MULTI_STATEMENTS, cursorclass=pymysql.cursors.DictCursor)

        cur = con.cursor()
        try:
            cur.execute("SELECT name, year_released FROM movies_tv")
            movie_uniques = cur.fetchall()
            movie_unique_key = [(row['name'], row['year_released']) for row in movie_uniques]
            movies_tb_insert_list = list(filter(lambda x: (x[0], x[4]) not in movie_unique_key, movies_tb_insert_list))
        except pymysql.err.IntegrityError:
            logging.error(f'Duplicate entries given to DB')
            print("Did not add duplicated values to DB")
        con.close()
        movies_tb_insert_statement = "INSERT INTO movies_tv (name, category, chart, duration, year_released, language, \
                                    awards, box_office, country, production) \
                                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
        ratings_tb_insert_statement = "INSERT INTO ratings (imdb_chart_rank, imdb_rating, num_of_votes, omdb_metascore) \
                                    VALUES (%s, %s, %s, %s);"
        person_tb_insert_statement = "INSERT INTO person (name) VALUES (%s);"
        person_role_tb_insert_statement = "INSERT INTO person_role (role) VALUES (%s);"

        # connect to the database
        con = pymysql.connect(user=cfg.USERNAME, password=cfg.PASSWORD, host=cfg.HOST, db=cfg.DATABASE,
                            client_flag=CLIENT.MULTI_STATEMENTS, cursorclass=pymysql.cursors.DictCursor)
        cur = con.cursor()
        try:
            cur.executemany(movies_tb_insert_statement, movies_tb_insert_list)
            cur.executemany(ratings_tb_insert_statement, ratings_tb_insert_list)
            cur.executemany(person_tb_insert_statement, person_tb_insert_list)
            cur.executemany(person_role_tb_insert_statement, person_role_tb_insert_list)
            con.commit()
            logging.info('Data successfully added to IMDBScrape Database')
        except pymysql.err.IntegrityError:
            logging.error(f'Duplicate entries given to DB')
            print("Did not add duplicated values to DB")
        chart_finish_time = round(time.perf_counter() - chart_start_time, 2)
        print(f'Total time for scraping {chart}: {chart_finish_time} seconds')


def main():
    """
    Main function of the module. Parses the different arguments given by command line.
    Executes the scraper function with the arguments given
    """
    parser = argparse.ArgumentParser(prog='IMDb_Scraper', description='Query the IMDb site')
    parser.add_argument("-c", "--column_name", nargs='+', help='Column Names',
                        choices=["chart", "imdb_chart_rank", "category", "title", "year", "rating", "number_of_votes", "director",
                                 "main_actors", "language", "country", "awards", "duration", "writer", "box_office",
                                 "omdb_metascore", "production", "genre", "chart", "all"], required=True)
    args = parser.parse_args()
    if 'all' in args.column_name:
        cols = ["chart", "imdb_chart_rank", "category", "title", "year", "rating", "number_of_votes", "director", "main_actors",
                "language", "country", "awards", "duration", "writer", "box_office", "omdb_metascore", "production",
                "genre"]
    else:
        cols = args.column_name
    with open('stdout.log', 'w', encoding="utf-8") as stdout_file:
        start_time = time.perf_counter()
        scraper(cols, stdout_file)
        finish_time = time.perf_counter() - start_time
        print(f'Total time for scraping: {round(finish_time, 2)} seconds')
        stdout_file.close()


if __name__ == '__main__':
    main()
