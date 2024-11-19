import logging

import colorlog


class BotLogger(object):
    def __init__(self):
        self.handler = colorlog.StreamHandler()
        self.logger = colorlog.getLogger('sekretarka')
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(self.handler)

    def info(self, message):
        self.logger.info(message)

    def warning(self, message):
        self.logger.warning(message)

    def error(self, error):
        self.logger.error(f'{error} ({error.__class__.__name__})')

    def critical(self, error):
        self.logger.critical(f'{error} ({error.__class__.__name__})')


logger = BotLogger()
