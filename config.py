import os
from dotenv import dotenv_values

class Configure:
    def __init__(self, path='.env'):
        """
        Initialize configuration loader with .env file path validation.
        
        Args:
            path (str): Path to .env configuration file. Defaults to '.env'.
        """
        # Validate configuration file path
        if not os.path.isfile(path):
            self._settings = {}
        else:
            self._settings = dotenv_values(path)
        
        # Normalize keys to lowercase for case-insensitive attribute access
        self._settings = {k.lower(): v for k, v in self._settings.items()}

    def __getattr__(self, name):
        """Enable attribute-style access to configuration values (e.g., config.color)"""
        if name in self._settings:
            return self._settings[name]
        raise AttributeError(f"'Configure' object has no attribute '{name}'")
