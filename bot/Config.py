
class Config(object):
    def __init__(self):
        self.owner = None
        self.co_owner = None
        self.bot_channel_names = []
        self.nsfw_channel_names = []
        self.female_roles = []
        self.special_permission_roles = []
        self.general_channel_cooldown_time = 0
        self.bot_command_prefix = None
        self.enable_developer_mode = False