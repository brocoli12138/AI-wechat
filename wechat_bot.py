from config import Config
from wechat_client import WechatClient
from LLM.responsor import Responsor
from LLM.debounce_pool import DebouncePool
from context.context_manager import ContextManager

from typing import Any, Dict
import threading
import time

class WechatBot:
    def __init__(self):
        self.config = Config()
        self.wechatclient = WechatClient(self.config, self._message_handler)
        self.responsor = Responsor(self.config)
        self.context_manager = ContextManager(self.config)
        self.debounce_pool = DebouncePool(self.config, self._debounce_handler)
        self.friendname_list = []
        self.stop_flag = 0
        self.stop_flag_lock = threading.Lock()
        self.loop_thread: threading.Thread = None

    def _message_handler(self, message: Dict[str, Any]) -> None:
        """{
                "user_id": user_id,
                "message": {"role":"user","content":msg}
            }"""
        # 收到消息以后先提交到防抖池
        self.debounce_pool.submit_message(message.user_id, message.message)        
    
    def _debounce_handler(self, user_id: str, message: Dict):
        # 从上下文管理器获取历史消息，然后和新消息一起发送给LLM
        history = self.context_manager.get(user_id)
        response = self.responsor.send_request(user_id, message, history)
        # 收到LLM响应之后先将用户消息加入到上下文管理器，然后将响应加入到上下文管理器
        self.context_manager.append(user_id, message)
        self.context_manager.append(user_id, response)

    def _event_loop(self):
        while True:
            with self.stop_flag_lock:
                if self.stop_flag == 1:
                    break
            time.sleep(0.1)

    def _load_listen_friendname_list(self, filename: str):
        with open(filename, 'r', encoding='utf-8') as file:
            lines = [line.strip() for line in file]  # 使用 strip() 去除换行符和空白字符
        self.friendname_list = lines

    def start_event_loop(self):
        # 先进行逻辑设定
        # 为所有列表中的人启动监听
        for name in self.friendname_list:
            res = self.wechatclient.startListen(name)
            if res:
                print(f"Listen {name} succeed!")
            else:
                print(f"Listen {name} failed!")
        # 然后开启一个事件循环
        self.loop_thread = threading.Thread(target=self._event_loop, daemon=False)
        pass

    def stop_event_loop(self):
        with self.stop_flag_lock:
                self.stop_flag = 1
        self.loop_thread.join()

if __name__ == "__main__":
    bot = WechatBot()
