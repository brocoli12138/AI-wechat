import json
import importlib.util
import os
from typing import Any, Dict, List, Union, Callable, Optional
from config import Config

class ToolManager:
    """
    LLM工具管理类，实现OpenAI风格的工具管理接口
    支持从JSON文件加载工具描述，并执行对应的工具实现
    """
    
    def __init__(self, config: Config):
        """
        初始化工具管理器
        
        Args:
            tools_description_path: 工具描述JSON文件路径
            config: 配置对象，必须包含tools_implementation_path属性
        """
        
        # 加载工具描述
        self.tools_description = self._load_tools_description(config.tools_description)
        
        # 加载工具实现
        self.tool_implementations = self._load_tool_implementations(config.tools_implementation)
    
    def _load_tools_description(self, path: str) -> List[Dict]:
        """
        加载工具描述JSON文件
        
        Args:
            path: JSON文件路径
            
        Returns:
            工具描述列表
        """
        if not os.path.exists(path):
            raise FileNotFoundError(f"Tools description file not found: {path}")
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                tools_data = json.load(f)
            
            # 确保工具描述是符合OpenAI格式的列表
            if isinstance(tools_data, dict) and "tools" in tools_data:
                tools_data = tools_data["tools"]
            
            if not isinstance(tools_data, list):
                raise ValueError("Tools description must be a list of tool definitions")
            
            return tools_data
        except Exception as e:
            raise ValueError(f"Error loading tools description: {str(e)}")
    
    def _load_tool_implementations(self, module_path: str) -> Dict[str, Callable]:
        """
        加载工具实现模块
        
        Args:
            module_path: Python模块文件路径
            
        Returns:
            工具名称到实现函数的映射字典
        """
        if not os.path.exists(module_path):
            raise FileNotFoundError(f"Tools implementation file not found: {module_path}")
        
        # 从路径生成模块名称
        module_name = f"tools_implementation_{hash(module_path)}"
        
        # 动态加载模块
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # 提取所有可调用的工具实现函数
        implementations = {}
        for name in dir(module):
            # 跳过内置属性和私有方法
            if name.startswith('_'):
                continue
            
            func = getattr(module, name)
            if callable(func):
                implementations[name] = func
        
        return implementations
    
    def get_tools(self) -> List[Dict]:
        """
        获取工具列表（OpenAI风格的工具描述）
        
        Returns:
            工具描述列表
        """
        return self.tools_description
    
    def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行指定的工具
        
        Args:
            tool_name: 工具名称
            arguments: 传递给工具的参数
            
        Returns:
            工具执行结果，格式为:
            {
                "name": tool_name,
                "content": 执行结果,
                "status": "success" | "error"
            }
        """
        # 检查工具是否存在
        if tool_name not in self.tool_implementations:
            return {
                "name": tool_name,
                "content": f"Tool '{tool_name}' not found",
                "status": "error"
            }
        
        try:
            # 执行工具
            tool_func = self.tool_implementations[tool_name]
            result = tool_func(**arguments)
            
            # 处理可能的异步函数
            if hasattr(result, '__await__'):
                import asyncio
                result = asyncio.get_event_loop().run_until_complete(result)
            
            return result
        except Exception as e:
            return  f"Error executing tool: {str(e)}"
