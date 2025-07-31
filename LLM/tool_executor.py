import importlib.util
import json
import os
import threading
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
from typing import Dict, Any


class ToolExecutor:
    def __init__(self, config: Any):
        self.config = config
        self._tool_cache = {}
        self._executor = ThreadPoolExecutor(max_workers=config.tool_thread_pool_size)
        self._tool_descriptions = self._load_tool_descriptions()

    def _load_tool_descriptions(self) -> Dict:
        try:
            with open(self.config.tools_description_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}

    def _load_tool_module(self, tool_name: str):
        if tool_name in self._tool_cache:
            return self._tool_cache[tool_name]

        module_path = os.path.join(
            self.config.tools_implementation_path,
            f"{tool_name}.py"
        )
        
        spec = importlib.util.spec_from_file_location(tool_name, module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        self._tool_cache[tool_name] = module
        return module

    def execute_tool(self, tool_name: str, arguments: Dict, call_id: str, user_id: str):
        if tool_name not in self._tool_descriptions:
            return {
                'call_id': call_id,
                'result': {'error': 'Tool not registered'},
                'user_id': user_id
            }

        try:
            module = self._load_tool_module(tool_name)
            func = getattr(module, tool_name)

            # 参数验证（简化版）
            if not all(k in arguments for k in self._tool_descriptions[tool_name].get('parameters', {})):
                raise ValueError("Missing required parameters")

            future = self._executor.submit(func, **arguments)
            result = future.result(timeout=self.config.tool_timeout)

            return {
                'call_id': call_id,
                'result': result,
                'user_id': user_id
            }
        except FutureTimeoutError:
            return {
                'call_id': call_id,
                'result': {'error': 'Execution timed out'},
                'user_id': user_id
            }
        except Exception as e:
            return {
                'call_id': call_id,
                'result': {'error': str(e)},
                'user_id': user_id
            }