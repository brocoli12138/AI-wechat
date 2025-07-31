import unittest
from unittest.mock import MagicMock, patch, call
import time
import threading
from queue import Queue
from collections import defaultdict
import json

# 导入实现模块
from debounce_pool import DebouncePool
from dispatcher import Dispatcher
from request_sender import RequestSender
from tool_executor import ToolExecutor


class TestDebouncePool(unittest.TestCase):
    def setUp(self):
        self.config = MagicMock()
        self.config.max_wait_duration = 0.1
        self.config.debounce_threshold = 3
        
        self.locker = MagicMock()
        self.context_manager = MagicMock()
        
        self.pool = DebouncePool(self.config, self.locker, self.context_manager)

    def test_new_user_initialization(self):
        self.pool.submit_message('user1', {'role': 'user', 'content': 'test'})
        self.assertIn('user1', self.pool._user_queues)
        self.assertEqual(self.pool._user_queues['user1'].qsize(), 1)
        self.locker.acquire_user_lock.assert_called_once_with('user1')

    def test_threshold_trigger(self):
        for i in range(3):
            self.pool.submit_message('user2', {'role': 'user', 'content': f'msg{i}'})
        
        # 等待worker线程执行
        time.sleep(0.2)
        self.context_manager.submit_request.assert_called_once()
        args = self.context_manager.submit_request.call_args[0]
        self.assertEqual(args[0], 'user2')
        self.assertEqual(len(args[1][0]['content']), 9)  # 3 messages concatenated

    def test_dynamic_reset(self):
        self.pool.submit_message('user3', {'role': 'user', 'content': 'msg1'})
        time.sleep(0.05)
        self.pool.submit_message('user3', {'role': 'user', 'content': 'msg2'})
        time.sleep(0.06)  # total 0.11 > 0.1
        
        # 应该只触发一次
        self.assertEqual(self.context_manager.submit_request.call_count, 1)


class TestDispatcher(unittest.TestCase):
    def setUp(self):
        self.debounce_pool = MagicMock()
        self.request_sender = MagicMock()
        self.tool_executor = MagicMock()
        self.context_manager = MagicMock()
        
        self.dispatcher = Dispatcher(
            self.debounce_pool,
            self.request_sender,
            self.tool_executor,
            self.context_manager
        )

    def test_tool_call_routing(self):
        response = {
            'tool_calls': [{
                'name': 'test_tool',
                'arguments': {'param': 'value'},
                'id': 'call_123'
            }]
        }
        self.dispatcher.handle_response('user1', response)
        
        self.tool_executor.execute_tool.assert_called_once_with(
            tool_name='test_tool',
            arguments={'param': 'value'},
            call_id='call_123',
            user_id='user1'
        )

    def test_retry_mechanism(self):
        self.dispatcher.handle_response('user1', {})
        self.assertEqual(self.dispatcher.retry_counts['user1'], 1)
        
        # 第三次重试后不再重试
        for _ in range(2):
            self.dispatcher.handle_response('user1', {})
        self.assertEqual(self.dispatcher.retry_counts['user1'], 3)
        self.dispatcher.handle_response('user1', {})
        self.assertEqual(self.dispatcher.retry_counts['user1'], 3)  # capped


class TestRequestSender(unittest.TestCase):
    @patch('builtins.open', new_callable=unittest.mock.mock_open)
    @patch('json.load')
    def test_system_prompt_fallback(self, mock_json, mock_open):
        mock_open.side_effect = FileNotFoundError
        mock_json.return_value = {"default": "Fallback prompt"}
        
        config = MagicMock()
        config.system_prompt_path = 'nonexistent.json'
        sender = RequestSender(config)
        
        self.assertEqual(sender.system_prompts['default'], "Fallback prompt")

    @patch('openai.OpenAI')
    def test_api_request_structure(self, mock_client):
        config = MagicMock()
        config.model_name = 'gpt-4'
        config.openai_key = 'test_key'
        
        sender = RequestSender(config)
        sender.submit_request('user1', [{'role': 'user', 'content': 'test'}])
        
        mock_client.return_value.chat.completions.create.assert_called_once()
        args = mock_client.return_value.chat.completions.create.call_args[1]
        self.assertEqual(args['model'], 'gpt-4')
        self.assertIn({'role': 'user', 'content': 'test'}, args['messages'])


class TestToolExecutor(unittest.TestCase):
    def setUp(self):
        self.config = MagicMock()
        self.config.tools_implementation_path = './tools'
        self.config.tool_thread_pool_size = 2
        self.config.tool_timeout = 0.1
        
        # 模拟工具描述文件
        self.config.tools_description_path = 'tools_desc.json'
        
    @patch('builtins.open', new_callable=unittest.mock.mock_open)
    @patch('json.load')
    def test_tool_execution(self, mock_json, mock_open):
        mock_json.return_value = [{
            'name': 'test_tool',
            'function': {
                'parameters': {'param': {}}
            }
        }]
        
        executor = ToolExecutor(self.config)
        
        # 模拟工具模块
        with patch('importlib.util.spec_from_file_location') as mock_spec:
            mock_module = MagicMock()
            mock_spec.return_value.loader.exec_module.return_value = mock_module
            
            result = executor.execute_tool(
                'test_tool',
                {'param': 'value'},
                'call_123',
                'user1'
            )
            
            self.assertEqual(result['call_id'], 'call_123')
            mock_module.test_tool.assert_called_once_with(param='value')

    def test_timeout_handling(self):
        executor = ToolExecutor(self.config)
        executor._tool_descriptions = {'slow_tool': {}}
        
        # 创建一个永远阻塞的工具函数
        def slow_func():
            time.sleep(1)
            return 'result'
        
        with patch('importlib.util.module_from_spec') as mock_module:
            type(mock_module.return_value).slow_tool = slow_func
            
            result = executor.execute_tool(
                'slow_tool',
                {},
                'call_456',
                'user1'
            )
            
            self.assertIn('error', result['result'])
            self.assertEqual(result['result']['error'], 'Execution timed out')

if __name__ == '__main__':
    unittest.main()