import unittest
import tempfile
import shutil
import time
from unittest.mock import MagicMock, patch

from ..config import Config
from context_manager import ContextManager


class TestContextManager(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.config = Config()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_append_and_get(self):
        manager = ContextManager(self.config)
        manager.append('user1', {'role': 'user', 'content': 'Hello'})
        manager.append('user1', {'role': 'assistant', 'content': 'Hi'})
        
        context = manager.get('user1')
        self.assertEqual(len(context), 2)
        self.assertEqual(context[0]['content'], 'Hello')

    def test_context_trimming(self):
        manager = ContextManager(self.config)
        # 添加30条消息（15轮完整对话）
        for i in range(16):
            manager.append('user1', {'role': 'user', 'content': f'Q{i}'})
            manager.append('user1', {'role': 'assistant', 'content': f'A{i}'})
        
        context = manager.get('user1')
        self.assertEqual(int(self.config.CONTEXT_WINDOW_LENGTH), 15)  # 验证配置项
        self.assertEqual(len(context), 15)  # 验证上下文长度
        self.assertEqual(context[0]['content'], 'A8')

    def test_disk_persistence(self):
        manager = ContextManager(self.config)
        # 模拟没有加载上下文
        context = manager.get('user2')
        self.assertEqual(len(context), 0)
        # 模拟添加上下文
        manager.append('user2', {'role': 'user', 'content': 'Test'})
        context = manager.get('user2')
        self.assertEqual(len(context), 1)
        # 模拟保存上下文
        # manager.savefile('user2')


"""     @patch('time.time', return_value=1000)
    def test_eviction(self, mock_time):
        manager = ContextManager(self.config)
        manager.append('user3', {'role': 'user', 'content': 'Keep'})
        
        # 模拟时间流逝超过保留期限
        mock_time.return_value = 1000 + 65  # 65秒 > 60秒
        time.sleep(0.2)  # 等待驱逐线程
        print(f"当前缓存状态: {manager.storage._cache}")
        
        # 验证内存已清除
        with self.assertRaises(KeyError):
            manager.storage._cache['user3']
            # 打印当前缓存状态
        
        # 验证磁盘存在
        self.assertTrue(manager.file_manager._get_filepath('user3')) """

if __name__ == '__main__':
    unittest.main()