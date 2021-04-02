from downloader import Downloader
from parser import Parser
import argparse
import pymysql.cursors
from pymysql.constants import CLIENT
from API import ApiQuery
import logging
import config as cfg

logging.basicConfig(filename='imdb_log_file.log',
                    format='%(asctime)s-%(levelname)s-FILE:%(filename)s-FUNC:%(funcName)s-LINE:%(lineno)d-%(message)s',
                    level=logging.INFO)


def scraper(column_names):
    """
    This function creates a Downloader class object, which gets access to IMDb, parses
    the site's content and prints the requested columns by the user to std output.
    :param column_names: IMDb columns requests by user
    :return: Movies/TV series data requests by user
    """

    # Creating separate downloader objects to access each page
    downloader_top_chart = Downloader()
    downloader_movie_meter = Downloader()
    downloader_tv_shows = Downloader()

    # and accessing each page
    contents_top_chart = downloader_top_chart.download(cfg._TOP_MOVIE_CHART)
    contents_movie_meter = downloader_movie_meter.download(cfg._MOVIE_METER)
    contents_tv_shows = downloader_tv_shows.download(cfg._TOP_TV)

    # creating parser objects for each page
    parser_top_chart = Parser(contents_top_chart, 'top_chart')
    parser_movie_meter = Parser(contents_movie_meter, 'movie_meter')
    parser_tv_shows = Parser(contents_tv_shows, 'tv_shows')

    # and an API object for each page
    api_top_chart = ApiQuery('api_top_chart')
    api_movie_meter = ApiQuery('api_movie_meter')
    api_tv_shows = ApiQuery('api_tv_shows')

    # Parsing contents from both pages and extracting matching content from API
    data_top_chart = parser_top_chart.parse_contents(column_names, api_top_chart)
    data_movie_meter = parser_movie_meter.parse_contents(column_names, api_movie_meter)
    data_tv_shows = parser_tv_shows.parse_contents(column_names, api_tv_shows)

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
        p = "&"
        title = movie.title
        if movie.duration != 'N/A':
            duration = int(movie.duration[:3])
        else:
            pass
        type = movie.type
        year = movie.year
        language = s.join(movie.language)
        awards = movie.awards
        box_office = movie.box_office
        country = s.join(movie.country)
        production = p.join(movie.production)

        imdb_chart_rank = movie.imdb_chart_rank
        rating = movie.rating
        number_of_votes = movie.number_of_votes
        omdb_metascore = str(movie.omdb_metascore)

        director = movie.director
        if movie.main_actors is not None:
            main_actors = movie.main_actors.split(',')

        movies_tb_insert_list.append((title, type, duration, year, language, awards, box_office, country, production))
        ratings_tb_insert_list.append((imdb_chart_rank, rating, number_of_votes, omdb_metascore))
        # to_person_table.append(main_actors)

    movies_tb_insert_statement = "INSERT INTO Movies_TV (name, type, duration, year_released, awards, box_office, country, language, production) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);"
    ratings_tb_insert_statement = "INSERT INTO Ratings (imdb_chart_rank, imdb_rating, num_of_votes, omdb_metascore) VALUES (%s, %s, %s, %s);"
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
