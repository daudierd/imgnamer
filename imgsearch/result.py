class SearchResult():
    """SearchResult class used for image search.

    Attributes:
        - dimensions: a pair of integers representing the dimensions of an image
        - title: title of the source link containing the image
        - location: link to the source of the image
        - snippet: a description of the image in its source context
    """
    def __init__(self, dimensions, title, location, snippet):
        self.dimensions = dimensions
        self.title = title
        self.location = location
        self.snippet = snippet
