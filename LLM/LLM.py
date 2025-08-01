from ..config import Config
from ..tools.tools_manager import ToolManager
from openai import OpenAI

class Responsor:
    def __init__(self, config: Config):
        self.tool_manager = ToolManager()
        self.openai_client = OpenAI(api_key=config.openai_key,
                                    base_url=config.openai_endpoint)
        self.temp_context = []