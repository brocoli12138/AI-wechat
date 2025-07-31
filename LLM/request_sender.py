import json
import os
from openai import OpenAI
from typing import Dict, List, Any


class RequestSender:
    def __init__(self, config: Any):
        self.config = config
        self.system_prompts: Dict[str, str] = {}
        self.tools_descriptions = []
        self._load_system_prompts()
        self._load_tools_descriptions()

    def _load_system_prompts(self):
        try:
            with open(self.config.system_prompt_path, 'r', encoding='utf-8') as f:
                self.system_prompts = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.system_prompts = {"default": "You are a helpful assistant"}

    def _load_tools_descriptions(self):
        try:
            with open(self.config.tools_description_path, 'r', encoding='utf-8') as f:
                tools = json.load(f)
                # 验证工具描述格式
                if not isinstance(tools, list) or not all('function' in t for t in tools):
                    raise ValueError("Invalid tools format")
                self.tools_descriptions = tools
        except Exception:
            self.tools_descriptions = []

    def submit_request(self, user_id: str, messages: List[Dict]):
        # 获取最新上下文（实际应通过context_manager，此处简化）
        full_history = messages
        
        # 插入系统提示词
        system_prompt = self.system_prompts.get(user_id, self.system_prompts.get("default", ""))
        if system_prompt:
            full_history.insert(0, {"role": "system", "content": system_prompt})

        # 创建OpenAI客户端
        client = OpenAI(
            api_key=self.config.openai_key,
            base_url=self.config.openai_endpoint
        )

        # 发送请求
        try:
            response = client.chat.completions.create(
                model=self.config.model_name,
                messages=full_history,
                tools=self.tools_descriptions if self.tools_descriptions else None,
                tool_choice="auto" if self.tools_descriptions else None
            )
            return response.choices[0].message.model_dump()
        except Exception as e:
            # 实际应触发调度员错误回调
            raise RuntimeError(f"API request failed: {str(e)}") from e