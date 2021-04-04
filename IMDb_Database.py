import logging
import pymysql.cursors
from pymysql.constants import CLIENT
import config as cfg

logging.basicConfig(filename='imdb_log_file.log',
                    format='%(asctime)s-%(levelname)s-FILE:%(filename)s-FUNC:%(funcName)s-LINE:%(lineno)d-%(message)s',
                    level=logging.INFO)

# Connecting to mysql
con = pymysql.connect(host=cfg.HOST, user=cfg.USERNAME, password=cfg.PASSWORD, client_flag=CLIENT.MULTI_STATEMENTS,
                      cursorclass=pymysql.cursors.DictCursor)

# Creating the database
cur = con.cursor()

q = """
CREATE DATABASE IF NOT EXISTS IMDBScrape;
 """

cur.execute(q)

con.commit()

con.close()
print('Successfully created IMDBScrape database')
logging.info('Successfully created IMDBScrape database')

con = pymysql.connect(host=cfg.HOST, user=cfg.USERNAME, password=cfg.PASSWORD, db=cfg.DATABASE, client_flag=CLIENT.MULTI_STATEMENTS,
                      cursorclass=pymysql.cursors.DictCursor)
# Creating the database tables
cur = con.cursor()

q1 = """
CREATE TABLE IF NOT EXISTS `Movies_TV` (
  `movie_sr_id` int PRIMARY KEY AUTO_INCREMENT,
  `category` varchar(10),
  `chart` varchar(40),
  `name` varchar(255),
  `year_released` varchar(4),
  `duration` int,
  `language` varchar(255),
  `description` varchar(1500),
  `country` varchar(255),
  `awards` varchar(355),
  `box_office` varchar(255),
  `production` varchar(355),
  CONSTRAINT uc_name_year UNIQUE (name, year_released)
);
CREATE TABLE IF NOT EXISTS `Person` (
  `person_id` int PRIMARY KEY AUTO_INCREMENT,
  `name` varchar(255),
  `birth_date` datetime,
  `height` int,
  `star_sign` varchar(255),
  `description` varchar(255)
);
CREATE TABLE IF NOT EXISTS `Person_role` (
  `person_id` int,
  `movie_sr_id` int,
  `role` varchar(255)
);
CREATE TABLE IF NOT EXISTS `Genres` (
  `genre_id` int PRIMARY KEY AUTO_INCREMENT,
  `genre_name` varchar(255),
  CONSTRAINT uc_genre_name UNIQUE (genre_name)
);
CREATE TABLE IF NOT EXISTS `Movie_genres` (
  `movie_sr_ID` int,
  `genre_id` int
);
CREATE TABLE IF NOT EXISTS `Reviewer` (
  `reviewer_id` int PRIMARY KEY AUTO_INCREMENT,
  `reviewer_name` varchar(255)
);
CREATE TABLE IF NOT EXISTS `Ratings` (
  `movie_sr_ID` int,
  `reviewer_id` int,
  `num_of_votes` varchar(50),
  `imdb_rating` float,
  `imdb_chart_rank` int,
  `omdb_metascore` varchar(50)
);
ALTER TABLE `Movie_genres` ADD FOREIGN KEY (`genre_id`) REFERENCES `Genres` (`genre_id`);
ALTER TABLE `Movie_genres` ADD FOREIGN KEY (`movie_sr_id`) REFERENCES `Movies_TV` (`movie_sr_id`);
ALTER TABLE `Ratings` ADD FOREIGN KEY (`reviewer_id`) REFERENCES `Reviewer` (`reviewer_id`);
ALTER TABLE `Ratings` ADD FOREIGN KEY (`movie_sr_id`) REFERENCES `Movies_TV` (`movie_sr_id`);
ALTER TABLE `Person_role` ADD FOREIGN KEY (`person_id`) REFERENCES `Person` (`person_id`);
ALTER TABLE `Person_role` ADD FOREIGN KEY (`movie_sr_id`) REFERENCES `Movies_TV` (`movie_sr_id`);
;
"""

cur.execute(q1)

con.commit()

con.close()
print('Successfully created IMDBScrape tables')
logging.info('Successfully created IMDBScrape tables')