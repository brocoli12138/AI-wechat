from .responsor import Responsor
from ..config import Config

config = Config()
responsor=Responsor(config)

res = responsor.send_request({"role":"user","content":"比较一下9.11和9.9的大小以及-3和-5的大小。"})
print(res)