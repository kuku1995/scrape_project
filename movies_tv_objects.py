class Item:
    """
    Creating objects of movies data
    """

    def __init__(self, category, imdb_chart_rank, title, year, rating, director, number_of_votes, main_actors, imdb_movie_id,
                 box_office, omdb_metascore, language, country, awards, duration, production, genre, writer, chart):
        self.category = category
        self.imdb_chart_rank = imdb_chart_rank
        self.title = title
        self.year = year
        self.rating = rating
        self.director = director
        self.writer = writer
        self.number_of_votes = number_of_votes
        self.main_actors = main_actors
        self.imdb_movie_id = imdb_movie_id
        self.language = language.split(',')
        self.country = country.split(',')
        self.awards = awards
        self.duration = duration
        self.box_office = box_office
        self.omdb_metascore = omdb_metascore
        self.production = production
        self.genre = genre
        self.chart = chart

    def format(self, column_names):
        """
        Formats the columns names for appearance and easier interaction
        :param column_names:
        :return: formatted column names
        """
        output = []
        for c in column_names:
            output.append(str(getattr(self, c)))
        return ', '.join(output)

    def __str__(self):
        return ((self.imdb_chart_rank + ' --> Title:' + self.title + ' --> Year:' + self.year + ' --> IMDB Rating:' +
                 str(self.rating) + '--> Number of voters:' + self.number_of_votes + '-->{Director:' + self.director +
                 ',' 'Starring:' + self.main_actors + ',' 'Language:' + self.language + ',' 'Country' + self.country + '}'))

    def __repr__(self):
        return self.__str__()
