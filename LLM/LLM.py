from ..config import Config
from ..tools.tools_manager import ToolManager
from openai import OpenAI
from typing import List, Dict, Any
from openai.types.chat import ChatCompletionMessageParam

class Responsor:
    def __init__(self, config: Config):
        self.tool_manager = ToolManager()
        self.openai_client = OpenAI(api_key=config.openai_key,
                                    base_url=config.openai_endpoint)
        self.temp_context: List[ChatCompletionMessageParam] = []