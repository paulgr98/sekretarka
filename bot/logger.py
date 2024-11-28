import logging


class BotLogger(object):
    def __init__(self):
        discord_formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(filename)s:%(lineno)d | %(message)s',
                                              datefmt='%H:%M:%S')
        app_formatter = logging.Formatter('%(asctime)s | %(filename)s:%(lineno)d | %(message)s',
                                          datefmt='%H:%M:%S')

        self.discord_logger = logging.getLogger('discord')
        self.discord_handler = logging.StreamHandler()
        self.discord_handler.setLevel(logging.ERROR)
        self.discord_handler.setFormatter(discord_formatter)
        self.discord_logger.addHandler(self.discord_handler)
        self.discord_logger.setLevel(logging.ERROR)
        self.discord_logger.propagate = False

        self.app_logger = logging.getLogger('app')
        self.app_handler = logging.StreamHandler()
        self.app_handler.setLevel(logging.DEBUG)
        self.app_handler.setFormatter(app_formatter)
        self.app_logger.addHandler(self.app_handler)
        self.app_logger.setLevel(logging.DEBUG)
        self.app_logger.propagate = False

    def error(self, error):
        self.discord_logger.error(f'{error} ({error.__class__.__name__})')

    def info(self, message):
        self.app_logger.info(message)

    def debug(self, message):
        self.app_logger.debug(message)


logger = BotLogger()
