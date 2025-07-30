import os
from dotenv import dotenv_values

class Config:
    def __init__(self, path=None):
        """
        Initialize configuration loader with .env file path validation.
        
        Args:
            path (str): Path to .env configuration file. Defaults to '.env'.
        """
        # 如果没有传路径，默认使用与 config.py 同级的 .env
        if path is None:
            # 获取当前文件（config.py）所在的目录
            current_dir = os.path.dirname(os.path.abspath(__file__))
            path = os.path.join(current_dir, '.env')
        
        # 检查配置文件是否存在
        if not os.path.isfile(path):
            raise FileNotFoundError(f"配置文件 {path} 不存在")
        self._settings = dotenv_values(path)
        # 检查配置项是否为空
        if not self._settings:
            raise ValueError("配置文件为空或未包含任何有效配置项")

        # 将所有配置键转换为小写，以实现大小写不敏感的访问
        self._settings = {k.lower(): v for k, v in self._settings.items()}

    def __getattr__(self, name):
        """Enable attribute-style access to configuration values (e.g., config.color)"""
        # 将属性名转换为小写以匹配配置键
        name = name.lower()
        if name in self._settings:
            return self._settings[name]
        # 如果配置项不存在，抛出AttributeError异常
        raise AttributeError(f"配置项 '{name}' 不存在")

    def __dir__(self):
        """返回所有可用的配置项名称"""
        return list(self._settings.keys())
