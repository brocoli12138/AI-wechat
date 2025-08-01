import threading
import time
from queue import Queue
from typing import Dict, Callable

from ..config import Config
from ..locker import Locker


class DebouncePool:
    def __init__(self, config: Config, request_callback: Callable[[str,Dict],None]) -> None:
        self.config = config
        self.locker = Locker() # 作用域就在本地，不能扩展到ContextManager
        self.request_callback = request_callback
        self._user_queues: Dict[str, Queue] = {}
        self._user_timers: Dict[str, float] = {}
        self._worker_threads: Dict[str, threading.Thread] = {}
        self._stop_events: Dict[str, threading.Event] = {}

    def submit_message(self, user_id: str, message: Dict) -> None:
        with self.locker.acquire_user_lock(user_id):
            if user_id not in self._user_queues:
                self._user_queues[user_id] = Queue()
                self._user_timers[user_id] = time.time()
                self._start_worker(user_id)
            
            self._user_queues[user_id].put(message)
            self._user_timers[user_id] = time.time()

            # 消息数达到阈值立即触发
            enable_request = self._user_queues[user_id].qsize() >= self.config.debounce_threshold

        if enable_request == True:
            # 发送请求必须在这里锁外执行，不然会死锁  
            self._trigger_request(user_id)

    def _start_worker(self, user_id: str) -> None:
        if user_id in self._worker_threads:
            return

        stop_event = threading.Event()
        self._stop_events[user_id] = stop_event

        def worker():
            while not stop_event.is_set():
                # 每次苏醒后获取锁并检查是否过期
                with self.locker.acquire_user_lock(user_id):
                    # 苏醒后如果user_quque已经没有user_id那说明已经触发过了
                    if user_id not in self._user_queues:
                        break
                    elapsed = time.time() - self._user_timers[user_id]
                remaining = max(0, self.config.max_wait_duration - elapsed)
                    
                if remaining > 0:
                    time.sleep(1)
                    continue

                self._trigger_request(user_id)
                break

        thread = threading.Thread(target=worker, daemon=True)
        self._worker_threads[user_id] = thread
        thread.start()

    def _trigger_request(self, user_id: str):
        with self.locker.acquire_user_lock(user_id):
            if user_id not in self._user_queues:
                return

            messages = []
            while not self._user_queues[user_id].empty():
                messages.append(self._user_queues[user_id].get())

            # 清理资源
            del self._user_queues[user_id]
            del self._user_timers[user_id]
            del self._worker_threads[user_id]
            del self._stop_events[user_id]

        # 拼接content，锁外执行提升性能
        content = ''.join(msg['content'] for msg in messages)
        self.request_callback(user_id, {"role": "user", "content": content})
        