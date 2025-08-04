from config import Config
from wxauto import WeChat, Chat
from wxauto.msgs import BaseMessage
from wxauto import WxParam
from typing import Any, Dict, Callable


class WechatClient:
    ''' A thread-unsafe unsafe unsafe WeChat client class '''
    wechat = WeChat()
    chatWindowList: Dict[str,Chat] = {}
    def __init__(self, config: Config, handler: Callable[[Dict[str, Any]], None]):
        self.config = config
        self.handler = handler
        WxParam.ENABLE_FILE_LOGGER = False
    
    def _on_message_(self, message: BaseMessage, chat: Chat) -> None:
        chatinfo = chat.ChatInfo()
        user_id = chatinfo.chat_name
        if message.sender!="self":
            if message.type == "text":
                msg = message.content
                WechatClient.handler({
                    "user_id": user_id,
                    "message": {"role":"user","content":msg}
                })
            elif message.type == "voice":
                msg = message.to_text()
                WechatClient.handler({
                    "user_id": user_id,
                    "message": {"role":"user","content":msg}
                })
            elif message.type == "time":
                timpoint = message.time
                msg = "Here is a time message. The time is " + timpoint + "."
                WechatClient.handler({
                    "user_id": user_id,
                    "message": {"role":"user","content":msg}
                })
            elif message.type == "emotion":
                msg = "Here is an emotion message to describe my emotion. You cannot understand it."
                WechatClient.handler({
                    "user_id": user_id,
                    "message": {"role":"user","content":msg}
                })
            elif message.type == "image":
                filepath = message.download(self.config.file_download_dir)
                msg = "Here is an image message. You can see it if you have a image viewer. The image is at " + filepath + "."
                WechatClient.handler({
                    "user_id": user_id,
                    "message": {"role":"user","content":msg}
                })
            elif message.type == "video":
                filepath = message.download(self.config.file_download_dir)
                msg = "Here is a video message. You can see it if you have a video viewer. The video is at " + filepath + "."
                WechatClient.handler({
                    "user_id": user_id,
                    "message": {"role":"user","content":msg}
                })
            elif message.type == "file":
                filepath = message.download(self.config.file_download_dir)
                msg = "Here is a file message. You can see it if you have a file viewer. The file is at " + filepath + "."
                WechatClient.handler({
                    "user_id": user_id,
                    "message": {"role":"user","content":msg}
                })
            else:
                msg = "Here is a complex message. You cannot understand it."
                WechatClient.handler({
                    "user_id": user_id,
                    "message": {"role":"user","content":msg}
                })

    def startListen(self, friendName: str) -> bool:
        if friendName in WechatClient.chatWindowList:
            print('Friend Exists!')
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
            WechatClient.chatWindowList[friendName].RemoveListenChat(friendName)
            del WechatClient.chatWindowList[friendName]
            return True
        else:
            print("Friend doesn't exist")
            return False
    
    @classmethod
    def sendTextMessage(friendName: str, message: str) -> bool:
        if friendName in WechatClient.chatWindowList:
            WechatClient.chatWindowList[friendName].SendMsg(message)
            return True
        else:
            print("Friend doesn't exist")
            return False
    
    @classmethod
    def sendFileMessage(friendName: str, filePath: str) -> bool:
        if friendName in WechatClient.chatWindowList:
            WechatClient.chatWindowList[friendName].SendFiles(filePath)
            return True
        else:
            print("Friend doesn't exist")
            return False
