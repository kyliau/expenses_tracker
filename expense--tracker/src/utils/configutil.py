import os
import json

currentDir = os.path.dirname(__file__)
srcDir = os.path.dirname(currentDir)
rootDir = os.path.dirname(srcDir)
CONFIG_FILE = os.path.join(rootDir, "config.json")
assert os.path.isfile(CONFIG_FILE)

with open(CONFIG_FILE) as configData:
    CONFIG = json.load(configData)

class ConfigUtil(object):
    """
    Namespace for utility functions that retrieve configuration
    parameters.
    """

    @staticmethod
    def get(key):
        """
        Return the value of the specified 'key' if it exists in the
        config file, otherwise return None.
        """
        return CONFIG.get(key, None)