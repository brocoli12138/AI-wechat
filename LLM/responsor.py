from config import Config
from tools.tools_manager import ToolManager
from openai import OpenAI
from typing import List, Dict, Any
import json

class Responsor:
    def __init__(self, config: Config):
        self.config=config
        self.tool_manager = ToolManager(config)
        self.openai_client = OpenAI(api_key=config.openai_key,
                                    base_url=config.openai_endpoint)
        self.temp_context = []
        self.system_prompt: Dict[str,str] = self._load_system_prompt(self.config.system_prompt_path)

    def _load_system_prompt(self, path: str) -> Dict[str,str]:
        """
        加载系统提示JSON文件
        
        Args:
            path: JSON文件路径
            
        Returns:
            系统提示字典
        """
        try:
            with open(path, 'r', encoding='utf-8') as file:
                system_prompt = json.load(file)
                if "default" not in system_prompt:
                    system_prompt["default"] = "You are an helpful assistant."
                return system_prompt
        except:
            return {"default": "You are an helpful assistant."}

    def _send_single_request(self):
        print(self.temp_context)
        response = self.openai_client.chat.completions.create(
                model=self.config.model_name,
                messages=self.temp_context,
                temperature=float(self.config.model_temperature),
                top_p=float(self.config.model_top_p),
                stream=False,
                tools=self.tool_manager.get_tools())
        
        return response.choices[0].message

    def send_request(self, user_id: str, new_message: Dict | None, history: List[Dict] = []) -> Dict:
        # 将历史和新消息拼接赋值给temp_context
        self.temp_context=history
        # 如果新消息不是None，说明是第一次调用，就拼接系统提示词之后将新消息添加到上下文
        if new_message != None:
            if user_id in self.system_prompt:
                self.temp_context.insert(0,{"role": "system", "content": self.system_prompt[user_id]})
            else:
                self.temp_context.insert(0,{"role": "system", "content": self.system_prompt["default"]})
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
                toolname=item.function.name
                toolargument=json.loads(item.function.arguments.strip())
                toolargument.update({"user_id": user_id})
                tool_res = self.tool_manager.execute_tool(toolname, toolargument)
                self.temp_context.append({"role": "tool", "content": tool_res,"tool_call_id": item.id})
            # 递归调用send_request，防止在提交tools工具之后LLM还需要调用工具。
            return self.send_request(user_id, None, self.temp_context)
        return {"role":res_message.role, "content":res_message.content}