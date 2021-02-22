from bs4 import BeautifulSoup
import requests
import re

website = 'http://www.imdb.com/chart/top'  # IMDb's Top 250 movies

access = requests.get(website)

soup = BeautifulSoup(access.text, 'lxml')

films = soup.select('td.titleColumn')

links = [link.attrs.get('href') for link in soup.select('td.titleColumn a')]

crew = [c.attrs.get('title') for c in soup.select('td.titleColumn a')]

IMDB_ratings = [rating.attrs.get('data-value') for rating in soup.select('td.posterColumn span[name=ir]')]

IMDB_num_of_user_ratings = [vote.attrs.get('data-value') for vote in soup.select('td.posterColumn span[name=nv]')]

# Tried scraping each movie url as well
# movies_length = []
# for link in links:
#     link = 'https://www.imdb.com/'+link
#     access = requests.get(link)
#     soup = BeautifulSoup(access.text, 'lxml')
#     length = [l.attrs.get('datetime') for l in soup.select('div.subtext time')]
#     length_of_movie = length[0][2:]
#     movies_length.append(length_of_movie)

imdb = []

for i in range(0, len(films)):

    raw_movie_title = films[i].get_text()
    movie = (' '.join(raw_movie_title.split()).replace('.', ''))
    title = movie[len(str(i))+1:-7]
    year = re.search('\((.*?)\)', raw_movie_title).group(1)
    rank = movie[:len(str(i))-(len(movie))]
    #link = 'https://www.imdb.com/' + links[i]
    #access = requests.get(link)
    #soup = BeautifulSoup(access.text, 'lxml')
    # length = soup.select('div.subtext time')
    data = {"movie_title": title,
            "year": year,
            "imdb_chart_rank": rank,
            "director": crew[i][0:crew[i].index('(')-1],
            "Main actors": crew[i][crew[i].index(')')+3:],
            "rating": round(float(IMDB_ratings[i]), 2),
            # "duration": length,
            "number_of_votes": "{:,}".format(int(IMDB_num_of_user_ratings[i]))}
    imdb.append(data)

for item in imdb:
    print(item['imdb_chart_rank'], '-->', item['movie_title'], '['+item['year']+'] --',
          'IMDB Rating:', item['rating'], '--', 'Number of voters:', item['number_of_votes'], '-- ' '{Director:', item['director']+',', 'Starring:', item['Main actors'], '}',)
          # '--', 'Duration of movie:', item['duration'],)

