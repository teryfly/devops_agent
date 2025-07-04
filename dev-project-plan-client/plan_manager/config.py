# Configuration manager for Plan Manager
from configparser import ConfigParser
import os

class ConfigManager:
    CONFIG_FILE = "plan_manager.ini"

    def __init__(self):
        self.config = ConfigParser()
        if os.path.exists(self.CONFIG_FILE):
            self.config.read(self.CONFIG_FILE)

    def get_config(self, key, default=None):
        return self.config.get('system', key, fallback=default)

    def set_config(self, key, value):
        if 'system' not in self.config:
            self.config['system'] = {}
        self.config['system'][key] = value
        with open(self.CONFIG_FILE, "w") as f:
            self.config.write(f)

    def get_database_config(self):
        db_keys = ['db_host', 'db_port', 'db_user', 'db_password', 'db_name']
        return {k: self.get_config(k) for k in db_keys}

    def get_retry_config(self):
        return {
            'retry_max_count': int(self.get_config('retry_max_count', 3)),
            'retry_wait_seconds': int(self.get_config('retry_wait_seconds', 60))
        }