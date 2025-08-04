from multiprocessing import set_forkserver_preload
import threading
import time
from queue import Queue
from typing import Dict, Callable

from config import Config
from locker import Locker


class DebouncePool:
    def __init__(self, config: Config, callback: Callable[[str,Dict],None]) -> None:
        self.config = config
        self.locker = Locker() # The scope is local and cannot be extended to ContextManager.
        self.callback = callback
        self._user_queues: Dict[str, Queue] = {}
        self._user_timers: Dict[str, float] = {}
        self._worker_threads: Dict[str, threading.Thread] = {}
        self._worker_threads_lock = threading.Lock()
        self._stop_events: Dict[str, threading.Event] = {}

    def submit_message(self, user_id: str, message: Dict) -> None:
        with self.locker.acquire_user_lock(user_id):
            if user_id not in self._user_queues:
                self._user_queues[user_id] = Queue()
                self._user_timers[user_id] = time.time()
                self._start_worker(user_id)
            
            self._user_queues[user_id].put(message)
            self._user_timers[user_id] = time.time()

            # Trigger immediately when the message count reaches the threshold
            enable_request = self._user_queues[user_id].qsize() >= self.config.debounce_threshold

        if enable_request == True:
            # Sending requests must be executed outside the lock here, otherwise it will deadlock 
            self._trigger(user_id)

    def _start_worker(self, user_id: str) -> None:
        with self._worker_threads_lock:
            if user_id in self._worker_threads:
                return

        stop_event = threading.Event()
        self._stop_events[user_id] = stop_event

        def worker():
            while not stop_event.is_set():
                # Acquire the lock and check for expiration after each wake-up
                with self.locker.acquire_user_lock(user_id):
                    # After waking up, if the user_queue no longer has a user_id, it means it has already been triggered.
                    if user_id not in self._user_queues:
                        break
                    elapsed = time.time() - self._user_timers[user_id]
                remaining = max(0, int(self.config.max_wait_duration) - elapsed)
                    
                if remaining > 0:
                    time.sleep(1)
                    continue

                self._trigger(user_id)
                break

        thread = threading.Thread(target=worker, daemon=True)
        self._worker_threads[user_id] = thread
        thread.start()

    def _trigger(self, user_id: str):
        with self.locker.acquire_user_lock(user_id):
            if user_id not in self._user_queues:
                return

            messages = []
            while not self._user_queues[user_id].empty():
                messages.append(self._user_queues[user_id].get())

            # Clean up resources
            del self._user_queues[user_id]
            del self._user_timers[user_id]
            del self._worker_threads[user_id]
            del self._stop_events[user_id]

        # Concatenate content, execute outside locks to improve performance
        content = ''.join(msg['content'] for msg in messages)
        self.callback(user_id, {"role": "user", "content": content})
        