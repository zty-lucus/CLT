# -*- coding: utf-8 -*-
"""
WebSocket事件测试用例
测试实时通信相关的WebSocket事件
"""
import pytest
import json
from unittest.mock import patch, MagicMock


class TestSendMessage:
    """测试发送消息事件"""

    def test_send_message_success(self, app, db_session, sample_conversation, sample_user):
        """测试成功发送消息"""
        with app.app_context():
            # 模拟SocketIO emit
            with patch('app.sockets.chat_events.emit') as mock_emit:
                from app.sockets.chat_events import handle_send_message

                # 准备测试数据
                data = {
                    'token': 'test-token',
                    'conversation_id': sample_conversation,
                    'msg_type': 1,
                    'content': 'Hello, World!'
                }

                # 模拟verify_token_from_socket
                with patch('app.sockets.chat_events.verify_token_from_socket') as mock_verify:
                    mock_verify.return_value = sample_user

                    # 调用处理函数
                    handle_send_message(data)

                    # 验证emit被调用
                    assert mock_emit.called

    def test_send_message_auth_failed(self, app, db_session):
        """测试认证失败"""
        with app.app_context():
            with patch('app.sockets.chat_events.emit') as mock_emit:
                from app.sockets.chat_events import handle_send_message

                data = {
                    'token': 'invalid-token',
                    'conversation_id': 1,
                    'msg_type': 1,
                    'content': 'Hello'
                }

                with patch('app.sockets.chat_events.verify_token_from_socket') as mock_verify:
                    mock_verify.return_value = None

                    handle_send_message(data)

                    # 验证发送了错误消息
                    mock_emit.assert_called_with('error', {'message': '认证失败'})

    def test_send_message_empty_content(self, app, db_session, sample_user):
        """测试空消息内容"""
        with app.app_context():
            with patch('app.sockets.chat_events.emit') as mock_emit:
                from app.sockets.chat_events import handle_send_message

                data = {
                    'token': 'test-token',
                    'conversation_id': 1,
                    'msg_type': 1,
                    'content': ''
                }

                with patch('app.sockets.chat_events.verify_token_from_socket') as mock_verify:
                    mock_verify.return_value = sample_user

                    handle_send_message(data)

                    # 验证发送了错误消息
                    mock_emit.assert_called_with('error', {'message': '消息内容不能为空'})

    def test_send_message_file_type(self, app, db_session, sample_conversation, sample_user):
        """测试发送文件类型消息"""
        with app.app_context():
            with patch('app.sockets.chat_events.emit') as mock_emit:
                from app.sockets.chat_events import handle_send_message

                data = {
                    'token': 'test-token',
                    'conversation_id': sample_conversation,
                    'msg_type': 2,
                    'content': 'test.pdf',
                    'file_id': 123
                }

                with patch('app.sockets.chat_events.verify_token_from_socket') as mock_verify:
                    mock_verify.return_value = sample_user

                    handle_send_message(data)

                    # 验证emit被调用
                    assert mock_emit.called


class TestMsgRead:
    """测试消息已读事件"""

    def test_msg_read_success(self, app, db_session, sample_conversation, sample_user):
        """测试成功标记已读"""
        with app.app_context():
            from app.sockets.chat_events import handle_msg_read

            data = {
                'token': 'test-token',
                'conversation_id': sample_conversation
            }

            with patch('app.sockets.chat_events.verify_token_from_socket') as mock_verify:
                mock_verify.return_value = sample_user

                with patch('app.services.message_service.MessageService.mark_read') as mock_mark:
                    handle_msg_read(data)

                    # 验证mark_read被调用
                    mock_mark.assert_called_once_with(sample_conversation, sample_user)

    def test_msg_read_auth_failed(self, app, db_session):
        """测试认证失败"""
        with app.app_context():
            from app.sockets.chat_events import handle_msg_read

            data = {
                'token': 'invalid-token',
                'conversation_id': 1
            }

            with patch('app.sockets.chat_events.verify_token_from_socket') as mock_verify:
                mock_verify.return_value = None

                # 应该直接返回，不调用mark_read
                handle_msg_read(data)

    def test_msg_read_missing_conversation_id(self, app, db_session, sample_user):
        """测试缺少会话ID"""
        with app.app_context():
            from app.sockets.chat_events import handle_msg_read

            data = {
                'token': 'test-token'
            }

            with patch('app.sockets.chat_events.verify_token_from_socket') as mock_verify:
                mock_verify.return_value = sample_user

                with patch('app.services.message_service.MessageService.mark_read') as mock_mark:
                    handle_msg_read(data)

                    # 验证mark_read没有被调用
                    mock_mark.assert_not_called()


class TestTyping:
    """测试正在输入事件"""

    def test_typing_success(self, app, db_session, sample_conversation, sample_user, sample_users):
        """测试成功发送正在输入状态"""
        with app.app_context():
            with patch('app.sockets.chat_events.emit') as mock_emit:
                from app.sockets.chat_events import handle_typing

                data = {
                    'token': 'test-token',
                    'conversation_id': sample_conversation
                }

                with patch('app.sockets.chat_events.verify_token_from_socket') as mock_verify:
                    mock_verify.return_value = sample_user

                    with patch('app.services.message_service.MessageService.get_member_ids') as mock_members:
                        mock_members.return_value = [sample_user, sample_users[0]]

                        handle_typing(data)

                        # 验证emit被调用（发送给其他成员）
                        assert mock_emit.called

    def test_typing_auth_failed(self, app, db_session):
        """测试认证失败"""
        with app.app_context():
            from app.sockets.chat_events import handle_typing

            data = {
                'token': 'invalid-token',
                'conversation_id': 1
            }

            with patch('app.sockets.chat_events.verify_token_from_socket') as mock_verify:
                mock_verify.return_value = None

                # 应该直接返回
                handle_typing(data)

    def test_typing_missing_conversation_id(self, app, db_session, sample_user):
        """测试缺少会话ID"""
        with app.app_context():
            from app.sockets.chat_events import handle_typing

            data = {
                'token': 'test-token'
            }

            with patch('app.sockets.chat_events.verify_token_from_socket') as mock_verify:
                mock_verify.return_value = sample_user

                # 应该直接返回
                handle_typing(data)


class TestJoinConversation:
    """测试加入会话房间事件"""

    def test_join_conversation_success(self, app, db_session, sample_conversation, sample_user):
        """测试成功加入会话房间"""
        with app.app_context():
            with patch('app.sockets.chat_events.join_room') as mock_join:
                from app.sockets.chat_events import handle_join_conversation

                data = {
                    'token': 'test-token',
                    'conversation_id': sample_conversation
                }

                with patch('app.sockets.chat_events.verify_token_from_socket') as mock_verify:
                    mock_verify.return_value = sample_user

                    handle_join_conversation(data)

                    # 验证join_room被调用
                    mock_join.assert_called_once_with(f'user_{sample_user}')

    def test_join_conversation_auth_failed(self, app, db_session):
        """测试认证失败"""
        with app.app_context():
            with patch('app.sockets.chat_events.join_room') as mock_join:
                from app.sockets.chat_events import handle_join_conversation

                data = {
                    'token': 'invalid-token',
                    'conversation_id': 1
                }

                with patch('app.sockets.chat_events.verify_token_from_socket') as mock_verify:
                    mock_verify.return_value = None

                    handle_join_conversation(data)

                    # 验证join_room没有被调用
                    mock_join.assert_not_called()

    def test_join_conversation_missing_conversation_id(self, app, db_session, sample_user):
        """测试缺少会话ID"""
        with app.app_context():
            with patch('app.sockets.chat_events.join_room') as mock_join:
                from app.sockets.chat_events import handle_join_conversation

                data = {
                    'token': 'test-token'
                }

                with patch('app.sockets.chat_events.verify_token_from_socket') as mock_verify:
                    mock_verify.return_value = sample_user

                    handle_join_conversation(data)

                    # 验证join_room没有被调用
                    mock_join.assert_not_called()
