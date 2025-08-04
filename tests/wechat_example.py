from wxauto import WeChat, Chat
from wxauto.msgs import BaseMessage
from wxauto import WxParam

def on_message(message: BaseMessage, chat: Chat) ->None:
    print(message.content, chat.ChatInfo(), message.sender)
    
WxParam.ENABLE_FILE_LOGGER = False

wechat = WeChat()

chat = wechat.AddListenChat("friend1", on_message)

chat.SendMsg("Hello")

wechat.KeepRunning()

# wechat.RemoveListenChat("friend1")