import threading
import weakref

class Locker:
    def __init__(self):
        self.user_locks_lock = threading.Lock()
        # Using weak references to automatically clean up unreferenced locks
        self.user_locks = weakref.WeakValueDictionary()

    def acquire_user_lock(self, user_id: str) -> threading.Lock:
        """Safely acquire a lock for a specific user"""
        # First check (without lock)
        try:
            return self.user_locks[user_id]
        except KeyError:
            with self.user_locks_lock:
                # Second Check (Locked)
                try:
                    return self.user_locks[user_id]
                except KeyError:
                    lock = threading.Lock()
                    self.user_locks[user_id] = lock
                    return lock
