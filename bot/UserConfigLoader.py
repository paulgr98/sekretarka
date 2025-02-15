import json

from bot.Config import Config
from bot.User import User


class UserConfigLoader(object):
    def __init__(self):
        self.config = None

    def load(self, file_path: str):
        self.config = Config()
        with open(file_path, 'r') as file:
            data = json.load(file)

        self.load_owner(data)
        self.load_co_owner(data)
        self.load_server(data)
        self.load_bot(data)

    def load_server(self, data):
        self.config.bot_channel_names = data['server']['bot_channel_names']
        self.config.nsfw_channel_names = data['server']['nsfw_channel_names']
        self.config.female_roles = data['server']['female_roles']
        self.config.special_permission_roles = data['server']['special_permission_roles']
        self.config.general_channel_cooldown_time = data['server']['general_channel_cooldown_time']

    def load_co_owner(self, data):
        co_owner = User()
        co_owner.id = data["user"]['co_owner']['id']
        co_owner.nick = data["user"]['co_owner']['nick']
        self.config.co_owner = co_owner

    def load_owner(self, data):
        owner = User()
        owner.id = data["user"]['owner']['id']
        owner.nick = data["user"]['owner']['nick']
        self.config.owner = owner

    def load_bot(self, data):
        bot_prefix = data['bot']['prefix']
        self.config.bot_command_prefix = bot_prefix
        is_developer_mode = data['bot']['enable_developer_mode']
        self.config.enable_developer_mode = is_developer_mode

    def get_config(self):
        if self.config is None:
            raise ValueError("Config is not loaded yet.")
        return self.config
