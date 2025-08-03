from LLM.responsor import Responsor
from config import Config

config = Config()
responsor=Responsor(config)

res = responsor.send_request("123",{"role":"user","content":"你的文件系统里有没有影片列表？发送给我看一下。"})
print(res)