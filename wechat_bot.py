from multiprocessing import context
from config import Config
from wechat_client import WechatClient
from LLM.responsor import Responsor
from LLM.debounce_pool import DebouncePool
from context.context_manager import ContextManager

from typing import Any, Dict, Callable
import threading
import time

class WechatBot:
    def __init__(self, frontend_handler: Callable[[str, Dict[str, Any]], None] = None):
        self.config = Config()
        self.wechatclient = WechatClient(self.config, self._message_handler)
        self.responsor = Responsor(self.config)
        self.context_manager = ContextManager(self.config)
        self.debounce_pool = DebouncePool(self.config, self._debounce_handler)
        self.frontend_handler = frontend_handler
        self.friendname_list = self._load_listen_friendname_list(self.config.listen_friendname_file)
        self.stop_flag = 0
        self.stop_flag_lock = threading.Lock()
        self.loop_thread: threading.Thread = None
    
    def _message_handler(self, message: Dict[str, Any]) -> None:
        """message: {
                "user_id": user_id,
                "message": {"role":"user","content":msg}
            }"""
        # First submit the message to the debounce pool upon receiving it
        self.debounce_pool.submit_message(message["user_id"], message["message"])        
    
    def _debounce_handler(self, user_id: str, message: Dict):
        # Retrieve historical messages from the context manager, then send them along with new messages to the LLM
        history = self.context_manager.get(user_id)
        response = self.responsor.send_request(user_id, message, history)
        # After receiving the LLM response, first add the user's message to the context manager, then add the response to the context manager
        self.context_manager.append(user_id, message)
        self.context_manager.append(user_id, response)
        # send response to user
        status = WechatClient.sendTextMessage(user_id, response["content"])
        # send response to frontend if frontend_handler is not None
        if self.frontend_handler != None:
            """frontend_handler(userid, Dict_message)
            Dict_message: {"role": "user", "content": msg}"""
            if status == True:
                self.frontend_handler(user_id, message)
                self.frontend_handler(user_id, response)
            else:
                self.frontend_handler(user_id, {"role": "bot", "content": "message send failed"})

    def _event_loop(self):
        while True:
            with self.stop_flag_lock:
                if self.stop_flag == 1:
                    break
            time.sleep(0.1)

    def _load_listen_friendname_list(self, filename: str):
        with open(filename, 'r', encoding='utf-8') as file:
            lines = [line.strip() for line in file]
        return lines

    def start_event_loop(self):
        # First, perform logical configuration
        # Start monitoring for all people in the list
        for name in self.friendname_list:
            res = self.wechatclient.startListen(name)
            if res:
                print(f"Listen {name} succeed!")
            else:
                print(f"Listen {name} failed!")
        # Then start an event loop
        self.loop_thread = threading.Thread(target=self._event_loop, daemon=False)
        self.loop_thread.start()

    def stop_event_loop(self):
        with self.stop_flag_lock:
                self.stop_flag = 1
        for name in self.friendname_list:
            res = self.wechatclient.stopListen(name)
            if res:
                print(f"Stop listen {name} succeed!")
            else:
                print(f"Stop listen {name} failed!")
        # Then join the event loop thread
        self.loop_thread.join()

if __name__ == "__main__":
    bot = WechatBot()
    bot.start_event_loop()
    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        bot.stop_event_loop()
