import threading
from typing import Dict, List, Dict as DictType

from config import Config
from storage_manager import StorageManager
from context_trimmer import ContextTrimmer
from file_manager import FileManager

class ContextManager:
    def __init__(self, config: Config) -> None:
        self.config = config
        self.file_manager = FileManager(config)
        self.storage = StorageManager(config, self.file_manager)
        self.trimmer = ContextTrimmer(config)
        self.user_locks: Dict[str, threading.Lock] = {}
        self.user_locks_lock = threading.Lock()
        self.storage.start_eviction_daemon()

    def _acquire_user_lock(self, user_id: str) -> threading.Lock:
        with self.user_locks_lock:
            if user_id not in self.user_locks:
                self.user_locks[user_id] = threading.Lock()
            return self.user_locks[user_id]

    def append(self, user_id: str, message: DictType) -> None:
        lock = self._acquire_user_lock(user_id)
        with lock:
            self.storage.add_context(user_id, message)

    def get(self, user_id: str) -> List[DictType]:
        lock = self._acquire_user_lock(user_id)
        with lock:
            full_context = self.storage.get_context(user_id)
            return self.trimmer.trim(full_context)

    def savefile(self, user_id: str) -> None:
        lock = self._acquire_user_lock(user_id)
        with lock:
            context = self.storage.get_context(user_id)
            self.file_manager.save_context(user_id, context)