import json
from tools_manager import ToolManager

def main():

    tool_manager = ToolManager()
    
    # 获取工具列表
    tools = tool_manager.get_tools()
    print("Available tools:", json.dumps(tools, indent=2))
    
    # 执行工具
    result = tool_manager.execute_tool("get_weather", {"location": "Beijing", 
        "unit": "fahrenheit"})
    print("\nTool execution result:", result)
    
    # 执行另一个工具
    result = tool_manager.execute_tool("search_web", {
        "query": "Python programming", 
        "num_results": 2
    })
    print("\nTool execution result:", result)

if __name__ == "__main__":
    main()
