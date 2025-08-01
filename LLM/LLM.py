from ..config import Config
from ..tools.tools_manager import ToolManager
from openai import OpenAI
from typing import List, Dict, Any

class Responsor:
    def __init__(self, config: Config):
        self.config=config
        self.tool_manager = ToolManager()
        self.openai_client = OpenAI(api_key=config.openai_key,
                                    base_url=config.openai_endpoint)
        self.temp_context = []

    def _send_single_request(self):
        response = self.openai_client.chat.completions.create(
                model=self.config.model_name,
                messages=self.temp_context,
                temperature=self.config.model_temperature,
                top_p=self.config.model_top_p,
                stream=False,
                tools=self.tool_manager.get_tools())
        
        return response.choices[0].message

    def send_request(self, user_id: str, new_message: Dict, history: List[Dict]) -> Dict:
        # 将历史和新消息拼接赋值给temp_context
        self.temp_context=history
        self.temp_context.append(new_message)
        # 发送一次单次请求
        res_message = self._send_single_request()
        # 检查是否是一般消息，如果是一般消息就返回，如果是工具调用，则逐个拼接响应之后再发送直到返回一般消息
        # 直到没有tool_calls 如果一开始就是一般消息，则不会进入while循环
        if res_message.tool_calls != None:
            # 先将tool_calls响应拼接进上下文，然后逐个执行tools
            self.temp_context.append(res_message)
            for item in res_message.tool_calls:
                # 逐个执行tools，然后拼接
                pass
        return {"role":res_message.role, "content":res_message.content}