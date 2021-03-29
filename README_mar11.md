# __IMDb Scraper Project__
![imdb logo](https://m.media-amazon.com/images/G/01/IMDb/BG_rectangle._CB1509060989_SY230_SX307_AL_.png)

## What is IMDb

The world's most popular and biggest online database of information related mostly
to films and TV series.

# Project purpose
Scarping movie relaed data from the IMDb website in order to analyze different variables which affect the movie rating on the site.

# How do we do it
We used the requests and BeautifulSoup modules in python in order to access the top 250 IMDb chart page's information, and selected the html tags relevant for the data we wanted.
We took the top 250 movies page for start and gathered different pieces of information for each movie, such as: Title, crew(director and star actors), the overall rating for each movie, its rank in the chart, the number of voters, and the year the movie was released. (More pending data will be added)
After doing so, we had a list of all 250 films, and ran a for loop on all movies to extract the relevant information for each film. Running the code gives an output of all the 250 films, with each film's relevant data on the same line (year, stars, etc).

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install requests, beautifulsoup4, html5lib, lxml

```bash
pip install requests
```

```bash
pip install beautifulsoup4
```

```bash
pip install html5lib
```

```bash
pip install lxml
```


### Usage

import requests
from bs4 import BeautifulSoup
import re

ACCESS = requests.get(WEBSITE) 
print(ACCESS) --> <Response [200]- means access to website data is approved  
SOUP = BeautifulSoup(ACCESS.text, 'lxml') - # parse the data from the website
FILMS = SOUP.select('td.titleColumn') - # returns container with film info

### Creating the Database
Make sure you install pymysql package
Run the database.py file in the directory, with your username and password to your localhost.
First query in this file creates the IMDb database.
Second query creates the tables according to scrapable information from IMDb.
Once doing so, running the IMBb_Scraper with the requested columns will insert the data to the Database.
Once creating the DB, each time running the scraper will add data to the DB.

### Running the program

Once Python is installed, best practice is to use the Pycharm IDE to open the main.py file.
Importing the required modules are necessary to run the program.

1) Get Access to the website as specified in the Usage section (requests.get)
2) Extracting all the movies using the soup method (FILMS example in Usage section)
3) Extracting the urls LINKS for each movie:
LINKS = [link.attrs.get('href') for link in SOUP.select('td.titleColumn a')]
4) Extracting the information regarding the movie crew (Directors, starts):
CREW = [c.attrs.get('title') for c in SOUP.select('td.titleColumn a')]
5) Extracting information regarding each movie rating:
IMDB_RATINGS = [rating.attrs.get('data-value') for rating in SOUP.select('td.posterColumn span[name=ir]')]
6) Next section (first for loop) handles structring all the movie data into a list of movies.
Each movie in the list is constrcuted as a dictionary with all its relevant info
7) Last section (second for loop) is for printing the information gathered to the screen

The output will print all the movies in this format:
61 --> Joker [2019] -- IMDB Rating: 8.37 -- Number of voters: 956,728 -- {Director: Todd Phillips, Starring: Joaquin Phoenix, Robert De Niro }

## Authors

* **Karishma Shah**
* **Lior Nattiv**

## Project status
In progress
