import os
import json
import base64
import shutil
import datetime
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
            # If the file already exists, append to the end of the old file
            # If the file does not exist, create it directly
            # Create temporary file path
            temp_filepath = filepath + '.tmp'
            
            try:
                # Write the content to a temporary file first
                with open(temp_filepath, 'w', encoding='utf-8') as f:
                    if os.path.exists(filepath):
                        # If the original file exists, first read the content of the original file
                        with open(filepath, 'r', encoding='utf-8') as original_file:
                            original_context = json.load(original_file)
                        if len(original_context) != 0:  
                            # If the original file is not empty, rename the old context
                            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                            os.replace(filepath, filepath + "." + timestamp + ".bak")
                    # Write new content
                    json.dump(context, f, ensure_ascii=False, indent=2)
                
                # Replace the original file using an atomic rename operation
                os.replace(temp_filepath, filepath)
                
            except Exception as e:
                # If an error occurs, clean up temporary files
                if os.path.exists(temp_filepath):
                    os.remove(temp_filepath)
                # Re-throw the exception to ensure the caller knows an error has occurred
                raise e


    def load_context(self, user_id: str) -> List[Dict]:
        filepath = self._get_filepath(user_id)
        if not os.path.exists(filepath):
            return []
        
        with self.file_locker.acquire_user_lock(user_id):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # If the message history exceeds 50, keep only the last 50
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