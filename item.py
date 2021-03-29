class Item:
    """
    Creating objects of movies data by columns requested by user
    """
    def __init__(self, imdb_chart_rank, movie_title, year, rating, director, number_of_votes, main_actors):
        self.imdb_chart_rank = imdb_chart_rank
        self.movie_title = movie_title
        self.year = year
        self.rating = rating
        self.director = director
        self.number_of_votes = number_of_votes
        self.main_actors = main_actors

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
        return ((self.imdb_chart_rank + ' --> ' + self.movie_title + '[' + self.year + '] --'
                'IMDB Rating:' + str(self.rating) + '--' + 'Number of voters:' + self.number_of_votes +
                '-- ' '{Director:' + self.director + ',' 'Starring:' + self.main_actors + '}'))

    def __repr__(self):
        return self.__str__()
