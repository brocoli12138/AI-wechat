from collections import defaultdict
import json
from typing import Dict, Any


class Dispatcher:
    def __init__(self, debounce_pool: Any, request_sender: Any, tool_executor: Any, context_manager: Any):
        self.debounce_pool = debounce_pool
        self.request_sender = request_sender
        self.tool_executor = tool_executor
        self.context_manager = context_manager
        self.retry_counts = defaultdict(int)

    def receive_message(self, user_id: str, message: Dict):
        """接收微信消息并持久化"""
        self.context_manager.append(user_id, message)
        self.debounce_pool.submit_message(user_id, message)

    def handle_response(self, user_id: str, response: Dict):
        """处理LLM响应并路由"""
        if 'tool_calls' in response:
            for tool_call in response['tool_calls']:
                self.tool_executor.execute_tool(
                    tool_name=tool_call['name'],
                    arguments=tool_call['arguments'],
                    call_id=tool_call['id'],
                    user_id=user_id
                )
        else:
            content = response.get('content')
            if not content:
                if self.retry_counts[user_id] < 3:
                    self.retry_counts[user_id] += 1
                    messages = self.context_manager.get(user_id)
                    self.request_sender.submit_request(user_id, messages)
                return
            
            self.context_manager.append(user_id, {
                'role': 'assistant',
                'content': content
            })
            # 实际应转发至微信操作员

    def handle_tool_result(self, tool_result: Dict):
        """处理工具执行结果并触发重试请求"""
        user_id = tool_result['user_id']
        call_id = tool_result['call_id']
        
        context = self.context_manager.get(user_id)
        context.append({
            'role': 'tool',
            'content': json.dumps(tool_result['result']),
            'tool_call_id': call_id
        })
        self.context_manager.set(user_id, context)
        
        self.request_sender.submit_request(user_id, context)