import time

from config import Config
from context.context_manager import ContextManager
def test_eviction():
    manager = ContextManager(Config())
    manager.append('user3', {'role': 'user', 'content': 'Keep'})
        
    time.sleep(0.2)
    print(f"当前缓存状态: {manager.storage._cache}")
        
    time.sleep(10)
    print(f"当前缓存状态: {manager.storage._cache}")

test_eviction()