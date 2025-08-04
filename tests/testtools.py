import json
from config import Config
from tools.tools_manager import ToolManager

def main():
    config = Config()
    tool_manager = ToolManager(config)
    
    tools = tool_manager.get_tools()
    print("Available tools:", json.dumps(tools, indent=2))
    
    result = tool_manager.execute_tool("list_files_in_directory", {"user_id": "123"})
    print("\nTool execution result:", result)
    
    result = tool_manager.execute_tool("send_a_file", {
        "file_name": "file_descriptions.txt",
        "user_id": "123"
    })
    print("\nTool execution result:", result)

if __name__ == "__main__":
    main()
