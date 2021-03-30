import logging
import requests
import re
from pprint import PrettyPrinter
pp = PrettyPrinter()

apiKey = 'b1e6e01b'

#Fetch Movie Data

data_URL = 'http://www.omdbapi.com/?apikey='+apiKey
year = ''
movieTitle = ''
params = {
    't': movieTitle,
    'type': 'movie',
    'y': year,
}
response = requests.get(data_URL, params=params).json()
pp.pprint(response.items())
#pp.pprint(response['Title'])
#pp.pprint(response(Actors))
#pp.pprint(response.json()['items'])