

class SearchResult():
    def __init__(self, img_height, img_width, title, location, snippet):
        self.dimensions['height'] = img_height
        self.dimensions['width'] = img_width
        self.title = title
        self.location = location
        self.snippet = snippet
