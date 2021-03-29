import pymysql.cursors
from pymysql.constants import CLIENT

# Connect to the database
username = 'root'
password = 'root'
host = 'localhost'
con = pymysql.connect(host=host, user=username, password=password, client_flag=CLIENT.MULTI_STATEMENTS,
                             cursorclass=pymysql.cursors.DictCursor)

cur = con.cursor()

q = """

CREATE DATABASE IF NOT EXISTS IMDBScrape;

 """


cur.execute(q)

con.commit()

con.close()


con = pymysql.connect(host=host, user=username, password=password, db='IMDBScrape', client_flag=CLIENT.MULTI_STATEMENTS,
                             cursorclass=pymysql.cursors.DictCursor)

cur = con.cursor()

q1 = """
CREATE TABLE IF NOT EXISTS `Movies` (
  `movie_ID` int PRIMARY KEY AUTO_INCREMENT,
  `name` varchar(255),
  `duration` int,
  `description` varchar(255),
  `rel_date` varchar(4)
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
  `movie_id` int,
  `role` varchar(255)
);


CREATE TABLE IF NOT EXISTS `Genres` (
  `genre_id` int PRIMARY KEY AUTO_INCREMENT,
  `genre_title` varchar(255)
);

CREATE TABLE IF NOT EXISTS `Movie_genres` (
  `movie_ID` int,
  `genre_id` int
);


CREATE TABLE IF NOT EXISTS `Reviewer` (
  `reviewer_id` int PRIMARY KEY AUTO_INCREMENT,
  `reviewer_name` varchar(255)
);

CREATE TABLE IF NOT EXISTS `Ratings` (
  `movie_ID` int,
  `reviewer_id` int,
  `no_of_votes` int,
  `no_of_stars` int
);

ALTER TABLE `Movie_genres` ADD FOREIGN KEY (`genre_id`) REFERENCES `Genres` (`genre_id`);

ALTER TABLE `Movie_genres` ADD FOREIGN KEY (`movie_ID`) REFERENCES `Movies` (`movie_ID`);

ALTER TABLE `Ratings` ADD FOREIGN KEY (`reviewer_id`) REFERENCES `Reviewer` (`reviewer_id`);

ALTER TABLE `Ratings` ADD FOREIGN KEY (`movie_ID`) REFERENCES `Movies` (`movie_ID`);

ALTER TABLE `Person_role` ADD FOREIGN KEY (`person_id`) REFERENCES `Person` (`person_id`);

ALTER TABLE `Person_role` ADD FOREIGN KEY (`movie_id`) REFERENCES `Movies` (`movie_ID`);
;

"""

cur.execute(q1)

con.commit()

con.close()