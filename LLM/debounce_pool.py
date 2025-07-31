import threading
import time
from queue import Queue
from typing import Dict, Any


class DebouncePool:
    def __init__(self, config: Any, locker: Any, context_manager: Any):
        self.config = config
        self.locker = locker
        self.context_manager = context_manager
        self._user_queues: Dict[str, Queue] = {}
        self._user_timers: Dict[str, float] = {}
        self._worker_threads: Dict[str, threading.Thread] = {}
        self._stop_events: Dict[str, threading.Event] = {}

    def submit_message(self, user_id: str, message: Dict):
        with self.locker.acquire_user_lock(user_id):
            if user_id not in self._user_queues:
                self._user_queues[user_id] = Queue()
                self._user_timers[user_id] = time.time()
                self._start_worker(user_id)
            
            self._user_queues[user_id].put(message)
            self._user_timers[user_id] = time.time()

            # 消息数达到阈值立即触发
            if self._user_queues[user_id].qsize() >= self.config.debounce_threshold:
                self._trigger_request(user_id)

    def _start_worker(self, user_id: str):
        if user_id in self._worker_threads:
            return

        stop_event = threading.Event()
        self._stop_events[user_id] = stop_event

        def worker():
            while not stop_event.is_set():
                elapsed = time.time() - self._user_timers[user_id]
                remaining = max(0, self.config.max_wait_duration - elapsed)
                
                if remaining > 0:
                    time.sleep(min(remaining, 0.1))
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

            # 拼接content
            content = ''.join(msg['content'] for msg in messages)
            self.context_manager.submit_request(user_id, [{"role": "user", "content": content}])

            # 清理资源
            del self._user_queues[user_id]
            del self._user_timers[user_id]
            del self._worker_threads[user_id]
            del self._stop_events[user_id]