from config import Config
import os
# from wechat_client import WechatClient


def list_files_in_directory(user_id: str) -> str:
    """List the files in the directory"""
    config = Config()
    files_dir = config.info_files_directory
    files = os.listdir(files_dir)
    # Filter out files (excluding directories)
    file_list = [f for f in files if os.path.isfile(os.path.join(files_dir, f))]
    files_str = "\n".join(file_list)
    # If a file_description.txt exists in the given path, append its content after "\n".join(file_list)
    if os.path.exists(os.path.join(files_dir, 'file_descriptions.txt')):
        with open(os.path.join(files_dir, 'file_descriptions.txt'), 'r', encoding='utf-8') as f:
            files_str += f"\n\nfile descriptions:\n{f.read()}"
            
    return files_str

def send_a_file(file_name: str, user_id:str) -> str:
    """Send files to users"""
    config = Config()
    files_dir = config.info_files_directory
    file_path = os.path.join(files_dir, file_name)
    if not os.path.exists(file_path):
        return f"File {file_name} not found"
    # Send File
    """ if WechatClient.sendFileMessage(self, user_id, file_path):
            return f"File {file_name} sent successfully!"
        else:
            return f"File {file_name} sent failed!" """
    return f"File {file_name} sent successfully"
