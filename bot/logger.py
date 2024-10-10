import logging

class BotLogger(object):
    def __init__(self):
        self.handler = logging.StreamHandler()
        self.logger = logging.getLogger('discord')


    def error(self, error):
        self.logger.error(f'{error} ({error.__class__.__name__})')


logger = BotLogger()
