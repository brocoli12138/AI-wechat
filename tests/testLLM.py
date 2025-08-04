from LLM.responsor import Responsor
from config import Config

config = Config()
responsor=Responsor(config)

res = responsor.send_request("123",{"role":"user","content":"Do you have a list of movies in your file system? Send it to me for a look."})
print(res)