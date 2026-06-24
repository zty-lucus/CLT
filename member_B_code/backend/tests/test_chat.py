# -*- coding: utf-8 -*-
"""
聊天路由测试用例
测试会话和消息相关的API
"""
import pytest
import json


class TestGetConversations:
    """测试获取会话列表"""

    def test_get_conversations_success(self, client, db_session, auth_headers, sample_conversation):
        """测试成功获取会话列表"""
        resp = client.get('/api/conversations', headers=auth_headers)
        data = resp.get_json()

        assert resp.status_code == 200
        assert data['code'] == 0
        assert 'data' in data
        assert isinstance(data['data'], list)

    def test_get_conversations_empty(self, client, db_session, auth_headers):
        """测试没有会话时获取列表"""
        resp = client.get('/api/conversations', headers=auth_headers)
        data = resp.get_json()

        assert resp.status_code == 200
        assert data['code'] == 0
        assert data['data'] == []

    def test_get_conversations_no_auth(self, client, db_session):
        """测试未认证时获取会话列表"""
        resp = client.get('/api/conversations')
        assert resp.status_code == 401


class TestGetConversationDetail:
    """测试获取会话详情"""

    def test_get_conversation_detail_success(self, client, db_session, auth_headers, sample_conversation):
        """测试成功获取会话详情"""
        conv_id = sample_conversation
        resp = client.get(f'/api/conversations/{conv_id}', headers=auth_headers)
        data = resp.get_json()

        assert resp.status_code == 200
        assert data['code'] == 0
        assert data['data']['id'] == conv_id
        assert 'members' in data['data']

    def test_get_conversation_detail_not_found(self, client, db_session, auth_headers):
        """测试获取不存在的会话详情"""
        resp = client.get('/api/conversations/999', headers=auth_headers)
        data = resp.get_json()

        assert resp.status_code == 200
        assert data['code'] == 1007

    def test_get_conversation_detail_no_auth(self, client, db_session, sample_conversation):
        """测试未认证时获取会话详情"""
        conv_id = sample_conversation
        resp = client.get(f'/api/conversations/{conv_id}')
        assert resp.status_code == 401


class TestCreatePrivateConversation:
    """测试创建单聊会话"""

    def test_create_private_conversation_success(self, client, db_session, auth_headers, sample_users):
        """测试成功创建单聊会话"""
        target_id = sample_users[0]
        resp = client.post('/api/conversations/private',
                          headers=auth_headers,
                          json={'target_id': target_id})
        data = resp.get_json()

        assert resp.status_code == 200
        assert data['code'] == 0
        assert 'id' in data['data']
        assert data['data']['type'] == 1

    def test_create_private_conversation_missing_target(self, client, db_session, auth_headers):
        """测试缺少目标用户ID"""
        resp = client.post('/api/conversations/private',
                          headers=auth_headers,
                          json={})
        data = resp.get_json()

        assert resp.status_code == 200
        assert data['code'] == 1001

    def test_create_private_conversation_nonexistent_user(self, client, db_session, auth_headers):
        """测试目标用户不存在"""
        resp = client.post('/api/conversations/private',
                          headers=auth_headers,
                          json={'target_id': 999})
        data = resp.get_json()

        assert resp.status_code == 200
        assert data['code'] == 1007

    def test_create_private_conversation_no_auth(self, client, db_session, sample_users):
        """测试未认证时创建会话"""
        target_id = sample_users[0]
        resp = client.post('/api/conversations/private',
                          json={'target_id': target_id})
        assert resp.status_code == 401


class TestGetMessages:
    """测试获取历史消息"""

    def test_get_messages_success(self, client, db_session, auth_headers, sample_conversation, app):
        """测试成功获取消息列表"""
        with app.app_context():
            # 创建测试消息
            for i in range(5):
                msg = app.Message(
                    conversation_id=sample_conversation,
                    sender_id=1,
                    msg_type=1,
                    content=f'Test message {i}'
                )
                app.db.session.add(msg)
            app.db.session.commit()

        conv_id = sample_conversation
        resp = client.get(f'/api/conversations/{conv_id}/messages',
                         headers=auth_headers)
        data = resp.get_json()

        assert resp.status_code == 200
        assert data['code'] == 0
        assert 'messages' in data['data']
        assert len(data['data']['messages']) == 5
        assert data['data']['total'] == 5

    def test_get_messages_pagination(self, client, db_session, auth_headers, sample_conversation, app):
        """测试消息分页"""
        with app.app_context():
            # 创建25条测试消息
            for i in range(25):
                msg = app.Message(
                    conversation_id=sample_conversation,
                    sender_id=1,
                    msg_type=1,
                    content=f'Test message {i}'
                )
                app.db.session.add(msg)
            app.db.session.commit()

        conv_id = sample_conversation

        # 第一页
        resp = client.get(f'/api/conversations/{conv_id}/messages?page=1&per_page=10',
                         headers=auth_headers)
        data = resp.get_json()
        assert len(data['data']['messages']) == 10
        assert data['data']['has_more'] is True

        # 第二页
        resp = client.get(f'/api/conversations/{conv_id}/messages?page=2&per_page=10',
                         headers=auth_headers)
        data = resp.get_json()
        assert len(data['data']['messages']) == 10

        # 第三页
        resp = client.get(f'/api/conversations/{conv_id}/messages?page=3&per_page=10',
                         headers=auth_headers)
        data = resp.get_json()
        assert len(data['data']['messages']) == 5
        assert data['data']['has_more'] is False

    def test_get_messages_not_member(self, client, db_session, auth_headers, app, sample_users):
        """测试非会话成员获取消息"""
        with app.app_context():
            # 创建一个用户不在的会话
            conv = app.Conversation(type=1, name='', creator_id=sample_users[0])
            app.db.session.add(conv)
            app.db.session.commit()
            conv_id = conv.id

        resp = client.get(f'/api/conversations/{conv_id}/messages',
                         headers=auth_headers)
        data = resp.get_json()

        assert resp.status_code == 200
        assert data['code'] == 1007

    def test_get_messages_no_auth(self, client, db_session, sample_conversation):
        """测试未认证时获取消息"""
        conv_id = sample_conversation
        resp = client.get(f'/api/conversations/{conv_id}/messages')
        assert resp.status_code == 401
