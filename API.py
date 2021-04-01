import logging
import requests
import config as cfg
logging.basicConfig(filename='imdb_log_file.log',
                    format='%(asctime)s-%(levelname)s-FILE:%(filename)s-FUNC:%(funcName)s-LINE:%(lineno)d-%(message)s',
                    level=logging.INFO)


class APIException(Exception):
    """
    Docstring
    """
    pass
# Fetch Movie Data


class ApiQuery:
    """
    Docstring
    """
    def query(self, imdb_movie_id):
        try:
            params = {
                'i': imdb_movie_id,
                'type': 'movie',
                'plot': 'full'
            }
            response = requests.get(cfg.API_DATA_URL, params=params).json()
            return response

        except Exception:
            logging.info('API not accessed successfully')
            raise APIException(" API not accessed successfully ")


   # def query_multiple(self, imdb_movie_ids):