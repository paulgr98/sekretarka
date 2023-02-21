import feedparser as fp


class Tvn24Feed(object):
    def __init__(self):
        self.url = None
        self.feed = None
        self.set_src_to_newest()

    def get_news(self):
        self.feed = fp.parse(self.url)
        return self.feed['entries']

    def set_src_to_newest(self):
        self.url = 'https://tvn24.pl/najnowsze.xml'

    def set_src_to_importants(self):
        self.url = 'https://tvn24.pl/najwazniejsze.xml'
