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
        Load system prompt JSON file
        
        Args:
            path: JSON file path
            
        Returns:
            System prompt dictionary
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
        # print(self.temp_context)
        response = self.openai_client.chat.completions.create(
                model=self.config.model_name,
                messages=self.temp_context,
                temperature=float(self.config.model_temperature),
                top_p=float(self.config.model_top_p),
                stream=False,
                tools=self.tool_manager.get_tools())
        
        return response.choices[0].message

    def send_request(self, user_id: str, new_message: Dict | None, history: List[Dict] = []) -> Dict:
        # Concatenate historical and new messages and assign them to temp_context
        self.temp_context=history
        # If the new message is not None, it means it's the first call, so concatenate the system prompt and then add the new message to the context
        if new_message != None:
            if user_id in self.system_prompt:
                self.temp_context.insert(0,{"role": "system", "content": self.system_prompt[user_id]})
            else:
                self.temp_context.insert(0,{"role": "system", "content": self.system_prompt["default"]})
            self.temp_context.append(new_message)
        # Send a single request
        res_message = self._send_single_request()
        # Check if it's a general message, return if true; if it's a tool call, concatenate responses one by one and resend until a general message is returned
        # Continue until there are no tool_calls. If it's a general message initially, the while loop won't be entered
        if res_message.tool_calls != None:
            # First concatenate the tool_calls response into the context, then execute the tools one by one
            self.temp_context.append(res_message)
            for item in res_message.tool_calls:
                # Execute tools one by one, then concatenate
                toolname=item.function.name
                toolargument=json.loads(item.function.arguments.strip())
                toolargument.update({"user_id": user_id})
                tool_res = self.tool_manager.execute_tool(toolname, toolargument)
                self.temp_context.append({"role": "tool", "content": tool_res,"tool_call_id": item.id})
            # Recursively call send_request to prevent the LLM from needing to call tools again after submitting the tools.
            return self.send_request(user_id, None, self.temp_context)
        return {"role":res_message.role, "content":res_message.content}