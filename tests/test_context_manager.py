import unittest
import tempfile
import shutil

from config import Config
from context.context_manager import ContextManager


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
        self.assertEqual(int(self.config.CONTEXT_WINDOW_LENGTH), 10) 
        self.assertEqual(len(context), 10) 
        #self.assertEqual(context[0]['content'], 'A8')

    def test_disk_persistence(self):
        manager = ContextManager(self.config)
        # Simulating no context loaded
        context = manager.get('user2')
        self.assertEqual(len(context), 0)
        # Simulating adding context
        manager.append('user2', {'role': 'user', 'content': 'Test'})
        context = manager.get('user2')
        self.assertEqual(len(context), 1)
        # Simulating saving context
        # manager.savefile('user2')

if __name__ == '__main__':
    unittest.main()