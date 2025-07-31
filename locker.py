import threading
import weakref

class Locker:
    def __init__(self):
        self.user_locks_lock = threading.Lock()
        # 使用弱引用自动清理无引用的锁
        self.user_locks = weakref.WeakValueDictionary()

    def acquire_user_lock(self, user_id: str) -> threading.Lock:
        """安全获取特定用户的锁"""
        # 第一次检查（无锁）
        try:
            return self.user_locks[user_id]
        except KeyError:
            with self.user_locks_lock:
                # 第二次检查（有锁）
                try:
                    return self.user_locks[user_id]
                except KeyError:
                    lock = threading.Lock()
                    self.user_locks[user_id] = lock
                    return lock
