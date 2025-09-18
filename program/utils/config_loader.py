import configparser
import os

config_path = os.path.join(os.path.dirname(__file__), '..', 'config.ini')
config = configparser.ConfigParser()
config.read(config_path, encoding='utf-8')