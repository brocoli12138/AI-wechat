from config import Config
from wxauto import WeChat, Chat
from wxauto.msgs import BaseMessage
from typing import Any, Dict, Callable


class WechatClient:
    ''' A thread-unsafe unsafe unsafe WeChat client class '''
    wechat = WeChat()
    chatWindowList: Dict[str,Chat] = {}
    def __init__(self, config: Config, handler: Callable[[Dict[str, Any]], None]):
        self.config = config
        self.handler = handler
    
    def _on_message_(self, message: BaseMessage, chat: Chat) -> None:
        user_id = chat.who
        if message.sender != "self":
            # 使用字典实现switch-case的效果
            message_switcher = {
                "text": lambda: message.content,
                "voice": lambda: message.to_text(),
                "emotion": lambda: "Here is an emotion message to describe my emotion.",
                "image": lambda: f"Here is an image message. You can see it if you have a image viewer. The image is at {message.download(self.config.file_download_dir)}.",
                "video": lambda: f"Here is a video message. You can see it if you have a video viewer. The video is at {message.download(self.config.file_download_dir)}.",
                "file": lambda: f"Here is a file message. You can see it if you have a file viewer. The file is at {message.download(self.config.file_download_dir)}."
            }

            # 获取消息内容，如果消息类型不在handlers中则返回默认消息
            msg = message_switcher.get(
                message.type,
                lambda: "[Between this square brackets is a invisiable non-text message. Please ignore it.]"
            )()

            # 调用处理函数
            self.handler({
                "user_id": user_id,
                "message": {"role": "user", "content": msg}
            })

    def startListen(self, friendName: str) -> bool:
        if friendName in WechatClient.chatWindowList:
            print(f'Friend {friendName} is already in listen!')
            return False
        else:
            chat = WechatClient.wechat.AddListenChat(friendName, self._on_message_)
            if isinstance(chat, Chat):
                WechatClient.chatWindowList[friendName] = chat
                return True
            else:
                return False

    def stopListen(self, friendName: str) -> bool:
        if friendName in WechatClient.chatWindowList:
            WechatClient.wechat.RemoveListenChat(friendName)
            del WechatClient.chatWindowList[friendName]
            return True
        else:
            print(f"Friend {friendName} is not in listen list!")
            return False
    
    @classmethod
    def sendTextMessage(cls, friendName: str, message: str) -> bool:
        if friendName in WechatClient.chatWindowList:
            WechatClient.chatWindowList[friendName].SendMsg(message)
            return True
        else:
            print(f"Friend {friendName} is not in listen list!")
            return False
    
    @classmethod
    def sendFileMessage(cls, friendName: str, filePath: str) -> bool:
        if friendName in WechatClient.chatWindowList:
            WechatClient.chatWindowList[friendName].SendFiles(filePath)
            return True
        else:
            print(f"Friend {friendName} is not in listen list!")
            return False
