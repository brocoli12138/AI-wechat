import os
import json
import base64
import shutil
from typing import List, Dict
from config import Config
from locker import Locker

class FileManager:
    def __init__(self, config: Config) -> None:
        self.storage_dir = config.context_storage_dir
        self.file_locker = Locker()
        os.makedirs(self.storage_dir, exist_ok=True)

    def _encode_filename(self, user_id: str) -> str:
        encoded = base64.urlsafe_b64encode(user_id.encode()).decode().rstrip('=')
        return f"{encoded}.json"

    def _get_filepath(self, user_id: str) -> str:
        filename = self._encode_filename(user_id)
        return os.path.join(self.storage_dir, filename)

    def save_context(self, user_id: str, context: List[Dict]) -> None:
        filepath = self._get_filepath(user_id)
        
        with self.file_locker.acquire_user_lock(user_id):
            # 如果已经存在这个文件，则追加在这个老文件的最后
            # 如果不存在这个文件，则直接创建这个文件
            # 创建临时文件路径
            temp_filepath = filepath + '.tmp'
            
            try:
                # 将内容先写入临时文件
                with open(temp_filepath, 'w', encoding='utf-8') as f:
                    if os.path.exists(filepath):
                        # 如果原文件存在，先读取原文件内容
                        with open(filepath, 'r', encoding='utf-8') as original:
                            original_content = original.read()
                            if original_content.strip():  # 如果原文件不为空
                                f.write(original_content)
                                if not original_content.endswith('\n'):
                                    f.write('\n')
                    
                    # 写入新的内容
                    json.dump(context, f, ensure_ascii=False, indent=2)
                
                # 使用原子性的重命名操作替换原文件
                os.replace(temp_filepath, filepath)
                
            except Exception as e:
                # 如果发生错误，清理临时文件
                if os.path.exists(temp_filepath):
                    os.remove(temp_filepath)
                # 重新抛出异常，确保调用者知道发生了错误
                raise e


    def load_context(self, user_id: str) -> List[Dict]:
        filepath = self._get_filepath(user_id)
        if not os.path.exists(filepath):
            return []
        
        with self.file_locker.acquire_user_lock(user_id):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # 如果消息记录超过50条，只保留最后50条
                    if isinstance(data, list) and len(data) > 50:
                        data = data[-50:]
                if not isinstance(data, list) or not all(isinstance(msg, dict) and 'role' in msg and 'content' in msg for msg in data):
                    raise ValueError("Invalid context structure")
                return data
            except (json.JSONDecodeError, ValueError):
                backup_path = f"{filepath}.bak"
                shutil.move(filepath, backup_path)
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump([], f)
                return []