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
        if user_id not in self.user_locks:
            with self.user_locks_lock:
                # 第二次检查（有锁）
                if user_id not in self.user_locks:
                    self.user_locks[user_id] = threading.Lock()
        return self.user_locks[user_id]