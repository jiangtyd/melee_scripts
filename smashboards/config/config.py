from ConfigParser import ConfigParser

DEFAULT_CONFIG_PATH = './config/config.ini'

class Config(object):
    def __init__(self, config_file_path=DEFAULT_CONFIG_PATH):
        self.config = ConfigParser()
        self.config.read(config_file_path)

    def get_db_host(self):
        return self.config.get('database', 'host')

    def get_db_user(self):
        return self.config.get('database', 'user')

    def get_db_password(self):
        return self.config.get('database', 'password')

    def get_db_name(self):
        return self.config.get('database', 'db_name')
