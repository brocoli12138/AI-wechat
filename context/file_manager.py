import os
import json
import base64
import shutil
from typing import List, Dict
from ..config import Config
from ..locker import Locker

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
        temp_path = f"{filepath}.tmp"
        
        with self.file_locker.acquire_user_lock(user_id):
            try:
                with open(temp_path, 'w', encoding='utf-8') as f:
                    json.dump(context, f, ensure_ascii=False, indent=2)
                shutil.move(temp_path, filepath)
            except Exception as e:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                raise

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