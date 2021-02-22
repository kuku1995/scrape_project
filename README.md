We are using the IMDb website, the world's most popular and biggest online database of information related mostly
to films and TV series.
We took the top 250 movies page for start and gathered different pieces of information for each movie, such as:
Title, crew(director and star actors), the overall rating for each movie, its rank in the chart, the number of voters,
and the year the movie was released. (More pending data will be added)
We used the requests and BeautifulSoup modules in python in order to access this specific page's information,
and selected the html tags relevant for the data we wanted.
After doing so, we had a list of all 250 films, and ran a for loop to extract the relevant information for each film.
Running the code gives an output of all the 250 films, with each film's relevant data on the same line (year, stars, etc).
​
​
check requirements.txt for all required installations and run the main.py file.
