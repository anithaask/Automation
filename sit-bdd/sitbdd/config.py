__all__ = ["Config"]

import json
import os
import sysconfig


def _find_data_dir(delivery_path: str, dev_name: str = "data", levels: int = 1) -> str:
    """Recurse up to find data directory if not at production path.

    :param delivery_path: Standard path in an end-user installation.
    :param dev_name: Directory name in development repository.
    :param levels: How many directories to recurse up.
    :return: Full path
    """

    dev_path = os.path.join(os.path.dirname(__file__), *([".."] * levels), dev_name)

    if os.path.isdir(delivery_path):
        return delivery_path
    elif os.path.isdir(dev_path):
        return dev_path
    else:
        raise FileNotFoundError("Could not find data directory")


class Config(dict):
    DATA_DIR = _find_data_dir(os.path.join(os.path.dirname(__file__), "data"))
    CONFIG_FILE_NAME = "config.json"
    CONFIG_USER_FILE_NAME = "config.user.json"

    def __init__(self, deployment: bool = False):
        super().__init__()
        self.data_dir = None
        self.config_file = None
        self.config_user_file = None
        self.set_config_location(deployment)
        self.load()


    def set_config_location(self, deployment: bool):
        """Set location of config file.

        :param deployment: True/False Config location is in deployment or development.
        """
        if deployment:
            self.data_dir = _find_data_dir(os.path.join(sysconfig.get_paths()["purelib"], 'sitbdd\data'))
            self.config_file = os.path.join(self.data_dir, self.CONFIG_FILE_NAME)
            self.config_user_file = os.path.join(self.data_dir, self.CONFIG_USER_FILE_NAME)
        else:
            self.data_dir = _find_data_dir(os.path.join(os.path.dirname(__file__), 'data'))
            self.config_file = os.path.join(self.data_dir, self.CONFIG_FILE_NAME)
            self.config_user_file = os.path.join(self.data_dir, self.CONFIG_USER_FILE_NAME)


    def load(self):
        """Load config from file.

        :return: None
        """

        self.clear()

        try:
            with open(self.config_user_file) as file:
                self.update(json.loads(file.read()))
        except FileNotFoundError:
            # fallback for when user config file doesn't exist, use unmodified config file.
            with open(self.config_file) as file:
                self.update(json.loads(file.read()))
