import json
import importlib.util
import os
from typing import Any, Dict, List, Union, Callable, Optional
from config import Config

class ToolManager:
    """
    LLM tool management class, implementing an OpenAI-style tool management interface
    Supports loading tool descriptions from JSON files and executing corresponding tool implementations
    """
    
    def __init__(self, config: Config):
        """
        Initialize the tool manager
        
        Args:
            tools_description_path: Path to the tool description JSON file
            config: Configuration object, must contain the tools_implementation_path attribute
        """
        self.config = config
        
        # Loading Tool Description
        self.tools_description = self._load_tools_description(r".\tools\default_descriptions.json")
        self.tools_description.extend(self._load_tools_description(self.config.tools_description_path))
        
        # Loading tool implementation
        self.tool_implementations = self._load_tool_implementations(r".\tools\default_implementations.py")
        self.tool_implementations.update(self._load_tool_implementations(self.config.tools_implementation_path))
    
    def _load_tools_description(self, path: str) -> List[Dict]:
        """
        Load tool description JSON file
        
        Args:
            path: JSON file path
            
        Returns:
            List of tool descriptions
        """
        if not os.path.exists(path):
            raise FileNotFoundError(f"Tools description file not found: {path}")
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                tools_data = json.load(f)
            
            # Ensure the tool description is in OpenAI-compliant list format
            if isinstance(tools_data, dict) and "tools" in tools_data:
                tools_data = tools_data["tools"]
            
            if not isinstance(tools_data, list):
                raise ValueError("Tools description must be a list of tool definitions")
            
            return tools_data
        except Exception as e:
            raise ValueError(f"Error loading tools description: {str(e)}")
    
    def _load_tool_implementations(self, module_path: str) -> Dict[str, Callable]:
        """
        Tool Implementation Module Loader
        
        Args:
            module_path: Path to the Python module file
            
        Returns:
            A dictionary mapping tool names to their implementation functions
        """
        if not os.path.exists(module_path):
            raise FileNotFoundError(f"Tools implementation file not found: {module_path}")
        
        # Generate module name from path
        module_name = f"tools_implementation_{hash(module_path)}"
        
        # Dynamic Module Loading
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Extract all callable tool implementation functions
        implementations = {}
        for name in dir(module):
            # Skip built-in attributes and private methods
            if name.startswith('_'):
                continue
            
            func = getattr(module, name)
            if callable(func):
                implementations[name] = func
        
        return implementations
    
    def get_tools(self) -> List[Dict]:
        """
        Get tool list (OpenAI-style tool descriptions)
        
        Returns:
            List of tool descriptions
        """
        return self.tools_description
    
    def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the specified tool
        
        Args:
            tool_name: Tool name
            arguments: Parameters passed to the tool
            
        Returns:
            Tool execution result
        """
        # Check if the tool exists
        if tool_name not in self.tool_implementations:
            return {
                "name": tool_name,
                "content": f"Tool '{tool_name}' not found",
                "status": "error"
            }
        
        try:
            # Execution Tool
            tool_func = self.tool_implementations[tool_name]
            result = tool_func(**arguments)
            
            # Handling possible asynchronous functions
            if hasattr(result, '__await__'):
                import asyncio
                result = asyncio.get_event_loop().run_until_complete(result)
            
            return result
        except Exception as e:
            return  f"Error executing tool: {str(e)}"
