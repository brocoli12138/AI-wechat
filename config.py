import os
from dotenv import dotenv_values

class Config:
    def __init__(self, path=None):
        """
        Initialize configuration loader with .env file path validation.
        
        Args:
            path (str): Path to .env configuration file. Defaults to '.env'.
        """
        # If no path is passed, the .env file at the same level as config.py is used by default
        if path is None:
            # Get the directory where the current file (config.py) is located
            current_dir = os.path.dirname(os.path.abspath(__file__))
            path = os.path.join(current_dir, '.env')
        
        # Check if the configuration file exists
        if not os.path.isfile(path):
            raise FileNotFoundError(f"The configuration file {path} does not exist.")
        self._settings = dotenv_values(path)
        # Check if configuration items are empty
        if not self._settings:
            raise ValueError("The configuration file is empty or does not contain any valid configuration items.")

        # Convert all configuration keys to lowercase for case-insensitive access
        self._settings = {k.lower(): v for k, v in self._settings.items()}

    def __getattr__(self, name):
        """Enable attribute-style access to configuration values (e.g., config.color)"""
        # Convert attribute names to lowercase to match configuration keys
        name = name.lower()
        if name in self._settings:
            return self._settings[name]
        # If the configuration item does not exist, raise an AttributeError exception
        raise AttributeError(f"Configuration item '{name}' does not exist")

    def __dir__(self):
        """Return all available configuration item names"""
        return list(self._settings.keys())
