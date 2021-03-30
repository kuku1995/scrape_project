import logging
import requests
logging.basicConfig(filename='imdb_log_file.log',
                    format='%(asctime)s-%(levelname)s-FILE:%(filename)s-FUNC:%(funcName)s-LINE:%(lineno)d-%(message)s',
                    level=logging.INFO)

# API Key for OMDb:
API_KEY = 'b1e6e01b'
API_DATA_URL = 'http://www.omdbapi.com/?apikey=' + API_KEY


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
    def query(imdb_movie_id):
        try:
            params = {
                'i': imdb_movie_id,
                'type': 'movie',
                'plot': 'full'
            }
            response = requests.get(API_DATA_URL, params=params).json()
        except:

