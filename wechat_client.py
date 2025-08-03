from config import Config
from wxauto import WeChat, Chat
from wxauto.msgs import BaseMessage
from wxauto import WxParam
from typing import Any, Dict, Callable

wechatobj = WeChat()

class WechatClient:
    def __init__(self, config: Config, handler: Callable[Dict[str, Any], None]):
        self.wechat = wechatobj
        self.config = config
        self.chatWindowList: Dict[str,Chat] = {}
        self.handler = handler
        WxParam.ENABLE_FILE_LOGGER = False
    
    def _on_message_(self, message: BaseMessage, chat: Chat) -> None:
        chatinfo = chat.ChatInfo()
        user_id = chatinfo.chat_name
        if message.sender!="self":
            if message.type == "text":
                msg = message.content
                self.handler({
                    "user_id": user_id,
                    "message": {"role":"user","content":msg}
                })
            elif message.type == "voice":
                msg = message.to_text()
                self.handler({
                    "user_id": user_id,
                    "message": {"role":"user","content":msg}
                })
            elif message.type == "time":
                timpoint = message.time
                msg = "Here is a time message. The time is " + timpoint + "."
                self.handler({
                    "user_id": user_id,
                    "message": {"role":"user","content":msg}
                })
            elif message.type == "emotion":
                msg = "Here is an emotion message to describe my emotion. You cannot understand it."
                self.handler({
                    "user_id": user_id,
                    "message": {"role":"user","content":msg}
                })
            elif message.type == "image":
                filepath = message.download(self.config.file_download_dir)
                msg = "Here is an image message. You can see it if you have a image viewer. The image is at " + filepath + "."
                self.handler({
                    "user_id": user_id,
                    "message": {"role":"user","content":msg}
                })
            elif message.type == "video":
                filepath = message.download(self.config.file_download_dir)
                msg = "Here is a video message. You can see it if you have a video viewer. The video is at " + filepath + "."
                self.handler({
                    "user_id": user_id,
                    "message": {"role":"user","content":msg}
                })
            elif message.type == "file":
                filepath = message.download(self.config.file_download_dir)
                msg = "Here is a file message. You can see it if you have a file viewer. The file is at " + filepath + "."
                self.handler({
                    "user_id": user_id,
                    "message": {"role":"user","content":msg}
                })
            else:
                msg = "Here is a complex message. You cannot understand it."
                self.handler({
                    "user_id": user_id,
                    "message": {"role":"user","content":msg}
                })

    def startListen(self, friendName: str) -> bool:
        chat = self.wechat.AddListenChat(friendName, self._on_message_)
        self.chatWindowList[friendName] = chat
        return True

    def stopListen(self, friendName: str) -> bool:
        if friendName in self.chatWindowList:
            self.chatWindowList[friendName].RemoveListenChat(friendName)
            del self.chatWindowList[friendName]
            return True
        else:
            print('好友不存在')
            return False
    
    def sendTextMessage(self, friendName: str, message: str) -> bool:
        if friendName in self.chatWindowList:
            self.chatWindowList[friendName].SendMsg(message)
            return True
        else:
            print('好友不存在')
            return False
    
    def sendFileMessage(self, friendName: str, filePath: str) -> bool:
        if friendName in self.chatWindowList:
            self.chatWindowList[friendName].SendFiles(filePath)
            return True
        else:
            print('好友不存在')
            return False
