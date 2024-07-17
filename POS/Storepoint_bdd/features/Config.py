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


class Config():
    DATA_DIR = _find_data_dir(os.path.join(os.path.dirname(__file__), "data"))
    CONFIG_FILE_NAME = "config.json"
    CONFIG_USER_FILE_NAME = "config.user.json"

    def __init__(self, deployment: bool = False):
        super().__init__()
        self.data_dir = None
        self.config_file = None
        self.config_user_file = None

