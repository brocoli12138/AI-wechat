import json
from config import Config
from tools.tools_manager import ToolManager

def main():
    config = Config()
    tool_manager = ToolManager(config)
    
    # 获取工具列表
    tools = tool_manager.get_tools()
    print("Available tools:", json.dumps(tools, indent=2))
    
    # 执行工具
    result = tool_manager.execute_tool("list_files_in_directory", {"user_id": "123"})
    print("\nTool execution result:", result)
    
    # 执行另一个工具
    result = tool_manager.execute_tool("send_a_file", {
        "file_name": "file_descriptions.txt",
        "user_id": "123"
    })
    print("\nTool execution result:", result)

if __name__ == "__main__":
    main()
