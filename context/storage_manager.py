import threading
import time
import copy
from typing import Dict, List, Tuple

from config import Config
from locker import Locker
from .file_manager import FileManager


class StorageManager:
    def __init__(self, config: Config, file_manager: FileManager) -> None:
        self.config = config
        self.file_manager = file_manager
        self._cache: Dict[str, Tuple[List[dict], float]] = {}
        self._locker = Locker()
        self._stop_event = threading.Event()

    def add_context(self, user_id: str, context: dict) -> None:
        with self._locker.acquire_user_lock(user_id):
            # If the user does not exist, try to load from the hard disk
            if user_id not in self._cache:
                self._cache[user_id] = (self.file_manager.load_context(user_id), time.time())
            # Get the current context list and add a new context
            current_contexts = self._cache[user_id][0]
            current_contexts.append(context)
            # Update cache and timestamp
            self._cache[user_id] = (current_contexts, time.time())

    def get_context(self, user_id: str) -> List[dict]:
        """Get user context information
        
        Args:
            user_id (str): User ID
            
        Returns:
            List[dict]: Deep copy of the user's context information list
            
        Notes:
            1. Use thread lock to ensure thread safety
            2. If the user's context is not in the cache, load it from the file
            3. Update the last access time of the user's context
            4. Return a deep copy of the context to prevent external modifications from affecting the cache
        """
        with self._locker.acquire_user_lock(user_id):
            # If the user context is not in the cache, load it from the file
            if user_id not in self._cache:
                self._cache[user_id] = (self.file_manager.load_context(user_id), time.time())
            # Update Last Access Time
            else:
                self._cache[user_id] = (self._cache[user_id][0], time.time())
            # Return a deep copy of the context
            return copy.deepcopy(self._cache[user_id][0])

    def _evict_expired_contexts(self) -> None:
        """
        Regularly check and clean up expired context cache
        
        This listener thread uses seconds as the unit for checking because:
        1. It needs to promptly respond to new user visits and reset the expiration time
        2. It needs to ensure data security by saving to file before deletion
        3. It needs to handle concurrent access scenarios
        """
        while not self._stop_event.is_set():
            time.sleep(min(int(self.config.context_stay_duration)/2, 60))
            now = time.time()
            # 1. Take a snapshot of cache keys (to avoid dictionary modification during traversal)
            uid_snapshot = list(self._cache.keys())
            
            for uid in uid_snapshot:
                with self._locker.acquire_user_lock(uid):
                    # 2. Secondary Verification: Check If the Cache Item Still Exists
                    if uid not in self._cache:
                        continue  # May have been deleted by another thread

                    # 3. Get the latest timestamp within the lock (to prevent timestamp expiration)
                    _, timestamp = self._cache[uid]
                    if (now - timestamp) >= int(self.config.context_stay_duration):
                        self.file_manager.save_context(uid, self._cache[uid][0])
                        del self._cache[uid]

    def start_eviction_daemon(self) -> None:
        thread = threading.Thread(target=self._evict_expired_contexts, daemon=True)
        thread.start()