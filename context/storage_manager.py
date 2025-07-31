import threading
import time
import copy
from typing import Dict, List, Tuple

from config import Config
from locker import Locker
from file_manager import FileManager


class StorageManager:
    def __init__(self, config: Config, file_manager: FileManager) -> None:
        self.config = config
        self.file_manager = file_manager
        self._cache: Dict[str, Tuple[List[dict], float]] = {}
        self._locker = Locker()
        self._stop_event = threading.Event()

    def add_context(self, user_id: str, context: dict) -> None:
        with self._locker.acquire_user_lock(user_id):
            # 如果用户不存在则创建新列表
            if user_id not in self._cache:
                self._cache[user_id] = ([], time.time())
            # 获取当前上下文列表并添加新的context
            current_contexts = self._cache[user_id][0]
            current_contexts.append(context)
            # 更新缓存和时间戳
            self._cache[user_id] = (current_contexts, time.time())

    def get_context(self, user_id: str) -> List[dict]:
        """获取用户上下文信息
        
        Args:
            user_id (str): 用户ID
            
        Returns:
            List[dict]: 用户的上下文信息列表的深拷贝
            
        说明:
            1. 使用线程锁保证线程安全
            2. 如果缓存中没有该用户的上下文,则从文件中加载
            3. 更新用户上下文的最后访问时间
            4. 返回上下文的深拷贝,避免外部修改影响缓存
        """
        with self._locker.acquire_user_lock(user_id):
            # 如果用户上下文不在缓存中,从文件加载
            if user_id not in self._cache:
                self._cache[user_id] = (self.file_manager.load_context(user_id), time.time())
            # 更新最后访问时间
            else:
                self._cache[user_id] = (self._cache[user_id][0], time.time())
            # 返回上下文的深拷贝
            return copy.deepcopy(self._cache[user_id][0])

    def _evict_expired_contexts(self) -> None:
        """
        定期检查并清理过期的上下文缓存
        
        这个监听线程使用秒为单位进行检查,因为:
        1. 需要及时响应用户的新访问,重置过期时间
        2. 需要保证数据安全性,在删除前保存到文件
        3. 需要处理并发访问的情况
        """
        while not self._stop_event.is_set():
            time.sleep(min(int(self.config.context_stay_duration)/2, 60))
            now = time.time()
            # 1. 获取缓存键的快照（避免遍历时字典被修改）
            uid_snapshot = list(self._cache.keys())
            
            for uid in uid_snapshot:
                with self._locker.acquire_user_lock(uid):
                    # 2. 二次验证：检查缓存项是否仍存在
                    if uid not in self._cache:
                        continue  # 可能已被其他线程删除
                        
                    # 3. 在锁内获取最新时间戳（防时间戳过期）
                    _, timestamp = self._cache[uid]
                    if (now - timestamp) >= int(self.config.context_stay_duration):
                        self.file_manager.save_context(uid, self._cache[uid][0])
                        del self._cache[uid]

    def start_eviction_daemon(self) -> None:
        thread = threading.Thread(target=self._evict_expired_contexts, daemon=True)
        thread.start()