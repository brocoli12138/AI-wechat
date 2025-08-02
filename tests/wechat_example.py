from wxauto import WeChat, Chat
from wxauto.msgs import BaseMessage
from wxauto import WxParam

def on_message(message: BaseMessage, chat: Chat) ->None:
    print(message.content, chat.ChatInfo(), message.sender)
    
WxParam.ENABLE_FILE_LOGGER = False

wechat = WeChat()

chat = wechat.AddListenChat("文件传输助手", on_message)

# 发送消息
chat.SendMsg("你好")


# 保持程序运行
wechat.KeepRunning()

# 移除监听
# wechat.RemoveListenChat("文件传输助手")