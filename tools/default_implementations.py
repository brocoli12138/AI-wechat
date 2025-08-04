from config import Config
import os
# from wechat_client import WechatClient


def list_files_in_directory(user_id: str) -> str:
    """列出目录下的文件"""
    config = Config()
    files_dir = config.info_files_directory
    files = os.listdir(files_dir)
    # 过滤出文件（排除目录）
    file_list = [f for f in files if os.path.isfile(os.path.join(files_dir, f))]
    files_str = "\n".join(file_list)
    # 如果路径中给存在file_description.txt文件，则将这个文件的内容追加在"\n".join(file_list)的后面
    if os.path.exists(os.path.join(files_dir, 'file_descriptions.txt')):
        with open(os.path.join(files_dir, 'file_descriptions.txt'), 'r', encoding='utf-8') as f:
            files_str += f"\n\n文件描述:\n{f.read()}"
            
    return files_str

def send_a_file(file_name: str, user_id:str) -> str:
    """发送文件给用户"""
    config = Config()
    files_dir = config.info_files_directory
    file_path = os.path.join(files_dir, file_name)
    if not os.path.exists(file_path):
        return f"File {file_name} not found"
    # 发送文件
    """ if WechatClient.sendFileMessage(self, user_id, file_path):
            return f"File {file_name} sent successfully!"
        else:
            return f"File {file_name} sent failed!" """
    return f"File {file_name} sent successfully"
