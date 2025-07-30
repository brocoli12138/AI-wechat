import copy
from typing import List, Dict

from config import Config

class ContextTrimmer:
    def __init__(self, config: Config) -> None:
        self.window_size = self._validate_window_size(config.context_window_length)

    def _validate_window_size(self, raw_size: int) -> int:
        return max(10, int(raw_size))

    def trim(self, full_history: List[Dict]) -> List[Dict]:
        if len(full_history) <= self.window_size:
            return copy.deepcopy(full_history)
        
        # 从最新消息开始截取
        trimmed = full_history[-self.window_size:]
        
        return trimmed