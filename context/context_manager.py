from typing import Dict, List
from ..config import Config
from storage_manager import StorageManager
from context_trimmer import ContextTrimmer
from file_manager import FileManager

class ContextManager:
    def __init__(self, config: Config) -> None:
        self.config = config
        self.file_manager = FileManager(config)
        self.storage = StorageManager(config, self.file_manager)
        self.trimmer = ContextTrimmer(config)
        self.storage.start_eviction_daemon()

    def append(self, user_id: str, message: Dict) -> None:
        self.storage.add_context(user_id, message)

    def get(self, user_id: str) -> List[Dict]:
        full_context = self.storage.get_context(user_id)
        return self.trimmer.trim(full_context)

    def savefile(self, user_id: str) -> None:
        context = self.storage.get_context(user_id)
        self.file_manager.save_context(user_id, context)