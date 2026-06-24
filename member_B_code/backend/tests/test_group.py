# -*- coding: utf-8 -*-
"""
群组路由测试用例
测试群组管理相关的API
"""
import pytest
import json


class TestGetGroups:
    """测试获取群组列表"""

    def test_get_groups_success(self, client, db_session, app, sample_users):
        """测试成功获取群组列表"""
        with app.app_context():
            # 使用第一个用户创建群组
            from flask_jwt_extended import create_access_token
            token = create_access_token(identity=str(sample_users[0]))
            headers = {'Authorization': f'Bearer {token}'}

            # 创建群组
            group = app.Conversation(
                type=2,
                name='Test Group',
                creator_id=sample_users[0]
            )
            app.db.session.add(group)
            app.db.session.flush()

            # 添加成员
            for user_id in sample_users:
                member = app.ConversationMember(
                    conversation_id=group.id,
                    user_id=user_id,
                    role=2 if user_id == sample_users[0] else 0
                )
                app.db.session.add(member)
            app.db.session.commit()

        resp = client.get('/api/groups', headers=headers)
        data = resp.get_json()

        assert resp.status_code == 200
        assert data['code'] == 0
        assert isinstance(data['data'], list)
        assert len(data['data']) > 0

    def test_get_groups_empty(self, client, db_session, auth_headers):
        """测试没有群组时获取列表"""
        resp = client.get('/api/groups', headers=auth_headers)
        data = resp.get_json()

        assert resp.status_code == 200
        assert data['code'] == 0
        assert data['data'] == []

    def test_get_groups_no_auth(self, client, db_session):
        """测试未认证时获取群组列表"""
        resp = client.get('/api/groups')
        assert resp.status_code == 401


class TestGetGroupDetail:
    """测试获取群组详情"""

    def test_get_group_detail_success(self, client, db_session, app, sample_users, sample_group):
        """测试成功获取群组详情"""
        with app.app_context():
            from flask_jwt_extended import create_access_token
            token = create_access_token(identity=str(sample_users[0]))
            headers = {'Authorization': f'Bearer {token}'}
        group_id = sample_group
        resp = client.get(f'/api/groups/{group_id}', headers=headers)
        data = resp.get_json()

        assert resp.status_code == 200
        assert data['code'] == 0
        assert data['data']['id'] == group_id
        assert 'members' in data['data']
        assert 'my_role' in data['data']

    def test_get_group_detail_not_found(self, client, db_session, auth_headers):
        """测试获取不存在的群组详情"""
        resp = client.get('/api/groups/999', headers=auth_headers)
        data = resp.get_json()

        assert resp.status_code == 200
        assert data['code'] == 1007

    def test_get_group_detail_not_member(self, client, db_session, auth_headers, app, sample_users):
        """测试非群成员获取群组详情"""
        with app.app_context():
            # 创建一个用户不在的群组
            group = app.Conversation(
                type=2,
                name='Other Group',
                creator_id=sample_users[0]
            )
            app.db.session.add(group)
            app.db.session.commit()
            group_id = group.id

        resp = client.get(f'/api/groups/{group_id}', headers=auth_headers)
        data = resp.get_json()

        assert resp.status_code == 200
        assert data['code'] == 1007


class TestCreateGroup:
    """测试创建群组"""

    def test_create_group_success(self, client, db_session, auth_headers, sample_users):
        """测试成功创建群组"""
        member_ids = sample_users[1:]
        resp = client.post('/api/groups',
                          headers=auth_headers,
                          json={
                              'name': 'New Group',
                              'member_ids': member_ids
                          })
        data = resp.get_json()

        assert resp.status_code == 200
        assert data['code'] == 0
        assert data['data']['name'] == 'New Group'
        assert data['data']['type'] == 2

    def test_create_group_missing_name(self, client, db_session, auth_headers):
        """测试缺少群组名称"""
        resp = client.post('/api/groups',
                          headers=auth_headers,
                          json={})
        data = resp.get_json()

        assert resp.status_code == 200
        assert data['code'] == 1001

    def test_create_group_no_auth(self, client, db_session, sample_users):
        """测试未认证时创建群组"""
        resp = client.post('/api/groups',
                          json={'name': 'Test Group'})
        assert resp.status_code == 401


class TestUpdateGroup:
    """测试修改群信息"""

    def test_update_group_success(self, client, db_session, app, sample_users, sample_group):
        """测试成功修改群信息"""
        with app.app_context():
            from flask_jwt_extended import create_access_token
            token = create_access_token(identity=str(sample_users[0]))
            headers = {'Authorization': f'Bearer {token}'}
        group_id = sample_group
        resp = client.put(f'/api/groups/{group_id}',
                         headers=headers,
                         json={
                             'name': 'Updated Group Name',
                             'announcement': 'New announcement'
                         })
        data = resp.get_json()

        assert resp.status_code == 200
        assert data['code'] == 0
        assert data['data']['name'] == 'Updated Group Name'
        assert data['data']['announcement'] == 'New announcement'

    def test_update_group_no_permission(self, client, db_session, app, sample_users):
        """测试无权限修改群信息"""
        with app.app_context():
            # 创建群组，使用第一个用户作为群主
            group = app.Conversation(
                type=2,
                name='Test Group',
                creator_id=sample_users[0]
            )
            app.db.session.add(group)
            app.db.session.flush()

            # 添加第二个用户为普通成员
            member = app.ConversationMember(
                conversation_id=group.id,
                user_id=sample_users[1],
                role=0
            )
            app.db.session.add(member)
            app.db.session.commit()

            # 使用普通成员的token
            from flask_jwt_extended import create_access_token
            token = create_access_token(identity=str(sample_users[1]))
            headers = {'Authorization': f'Bearer {token}'}

            group_id = group.id

        resp = client.put(f'/api/groups/{group_id}',
                         headers=headers,
                         json={'name': 'New Name'})
        data = resp.get_json()

        assert resp.status_code == 200
        assert data['code'] == 1006

    def test_update_group_not_found(self, client, db_session, app, sample_users):
        """测试修改不存在的群组"""
        with app.app_context():
            from flask_jwt_extended import create_access_token
            token = create_access_token(identity=str(sample_users[0]))
            headers = {'Authorization': f'Bearer {token}'}
        resp = client.put('/api/groups/999',
                         headers=headers,
                         json={'name': 'New Name'})
        data = resp.get_json()

        assert resp.status_code == 200
        assert data['code'] == 1006


class TestGetGroupMembers:
    """测试获取群成员列表"""

    def test_get_group_members_success(self, client, db_session, app, sample_users, sample_group):
        """测试成功获取群成员列表"""
        with app.app_context():
            from flask_jwt_extended import create_access_token
            token = create_access_token(identity=str(sample_users[0]))
            headers = {'Authorization': f'Bearer {token}'}
        group_id = sample_group
        resp = client.get(f'/api/groups/{group_id}/members', headers=headers)
        data = resp.get_json()

        assert resp.status_code == 200
        assert data['code'] == 0
        assert isinstance(data['data'], list)
        assert len(data['data']) == len(sample_users)

    def test_get_group_members_not_member(self, client, db_session, app, sample_users):
        """测试非群成员获取成员列表"""
        with app.app_context():
            # 创建一个用户不在的群组
            group = app.Conversation(
                type=2,
                name='Other Group',
                creator_id=sample_users[0]
            )
            app.db.session.add(group)
            app.db.session.commit()

            from flask_jwt_extended import create_access_token
            token = create_access_token(identity=str(sample_users[1]))
            headers = {'Authorization': f'Bearer {token}'}

            group_id = group.id

        resp = client.get(f'/api/groups/{group_id}/members', headers=headers)
        data = resp.get_json()

        assert resp.status_code == 200
        assert data['code'] == 1007


class TestInviteMembers:
    """测试邀请成员"""

    def test_invite_members_success(self, client, db_session, app, sample_users):
        """测试成功邀请成员"""
        with app.app_context():
            # 创建群组
            group = app.Conversation(
                type=2,
                name='Test Group',
                creator_id=sample_users[0]
            )
            app.db.session.add(group)
            app.db.session.flush()

            # 添加群主
            owner = app.ConversationMember(
                conversation_id=group.id,
                user_id=sample_users[0],
                role=2
            )
            app.db.session.add(owner)
            app.db.session.commit()

            from flask_jwt_extended import create_access_token
            token = create_access_token(identity=str(sample_users[0]))
            headers = {'Authorization': f'Bearer {token}'}

            # 创建新用户用于邀请
            new_user = app.User(username='newuser', nickname='New User')
            app.db.session.add(new_user)
            app.db.session.commit()

            group_id = group.id
            new_user_id = new_user.id

        resp = client.post(f'/api/groups/{group_id}/members',
                          headers=headers,
                          json={'user_ids': [new_user_id]})
        data = resp.get_json()

        assert resp.status_code == 200
        assert data['code'] == 0
        assert new_user_id in data['data']['added_members']

    def test_invite_members_missing_ids(self, client, db_session, app, sample_users, sample_group):
        """测试缺少被邀请用户ID"""
        with app.app_context():
            from flask_jwt_extended import create_access_token
            token = create_access_token(identity=str(sample_users[0]))
            headers = {'Authorization': f'Bearer {token}'}
        group_id = sample_group
        resp = client.post(f'/api/groups/{group_id}/members',
                          headers=headers,
                          json={})
        data = resp.get_json()

        assert resp.status_code == 200
        assert data['code'] == 1001

    def test_invite_members_not_member(self, client, db_session, app, sample_users):
        """测试非群成员邀请"""
        with app.app_context():
            # 创建群组
            group = app.Conversation(
                type=2,
                name='Test Group',
                creator_id=sample_users[0]
            )
            app.db.session.add(group)
            app.db.session.commit()

            from flask_jwt_extended import create_access_token
            token = create_access_token(identity=str(sample_users[1]))
            headers = {'Authorization': f'Bearer {token}'}

            group_id = group.id

        resp = client.post(f'/api/groups/{group_id}/members',
                          headers=headers,
                          json={'user_ids': [sample_users[2]]})
        data = resp.get_json()

        assert resp.status_code == 200
        assert data['code'] == 1006


class TestRemoveMember:
    """测试踢出群成员"""

    def test_remove_member_success(self, client, db_session, app, sample_users):
        """测试成功踢出群成员"""
        with app.app_context():
            # 创建群组
            group = app.Conversation(
                type=2,
                name='Test Group',
                creator_id=sample_users[0]
            )
            app.db.session.add(group)
            app.db.session.flush()

            # 添加群主
            owner = app.ConversationMember(
                conversation_id=group.id,
                user_id=sample_users[0],
                role=2
            )
            app.db.session.add(owner)

            # 添加普通成员
            member = app.ConversationMember(
                conversation_id=group.id,
                user_id=sample_users[1],
                role=0
            )
            app.db.session.add(member)
            app.db.session.commit()

            from flask_jwt_extended import create_access_token
            token = create_access_token(identity=str(sample_users[0]))
            headers = {'Authorization': f'Bearer {token}'}

            group_id = group.id
            target_id = sample_users[1]

        resp = client.delete(f'/api/groups/{group_id}/members/{target_id}',
                            headers=headers)
        data = resp.get_json()

        assert resp.status_code == 200
        assert data['code'] == 0

    def test_remove_member_no_permission(self, client, db_session, app, sample_users):
        """测试无权限踢出成员"""
        with app.app_context():
            # 创建群组
            group = app.Conversation(
                type=2,
                name='Test Group',
                creator_id=sample_users[0]
            )
            app.db.session.add(group)
            app.db.session.flush()

            # 添加群主
            owner = app.ConversationMember(
                conversation_id=group.id,
                user_id=sample_users[0],
                role=2
            )
            app.db.session.add(owner)

            # 添加普通成员
            member1 = app.ConversationMember(
                conversation_id=group.id,
                user_id=sample_users[1],
                role=0
            )
            member2 = app.ConversationMember(
                conversation_id=group.id,
                user_id=sample_users[2],
                role=0
            )
            app.db.session.add_all([member1, member2])
            app.db.session.commit()

            # 使用普通成员1的token尝试踢出成员2
            from flask_jwt_extended import create_access_token
            token = create_access_token(identity=str(sample_users[1]))
            headers = {'Authorization': f'Bearer {token}'}

            group_id = group.id
            target_id = sample_users[2]

        resp = client.delete(f'/api/groups/{group_id}/members/{target_id}',
                            headers=headers)
        data = resp.get_json()

        assert resp.status_code == 200
        assert data['code'] == 1006

    def test_remove_group_owner(self, client, db_session, app, sample_users):
        """测试踢出群主"""
        with app.app_context():
            # 创建群组
            group = app.Conversation(
                type=2,
                name='Test Group',
                creator_id=sample_users[0]
            )
            app.db.session.add(group)
            app.db.session.flush()

            # 添加群主
            owner = app.ConversationMember(
                conversation_id=group.id,
                user_id=sample_users[0],
                role=2
            )
            app.db.session.add(owner)

            # 添加管理员
            admin = app.ConversationMember(
                conversation_id=group.id,
                user_id=sample_users[1],
                role=1
            )
            app.db.session.add(admin)
            app.db.session.commit()

            # 使用管理员token尝试踢出群主
            from flask_jwt_extended import create_access_token
            token = create_access_token(identity=str(sample_users[1]))
            headers = {'Authorization': f'Bearer {token}'}

            group_id = group.id
            target_id = sample_users[0]

        resp = client.delete(f'/api/groups/{group_id}/members/{target_id}',
                            headers=headers)
        data = resp.get_json()

        assert resp.status_code == 200
        assert data['code'] == 1006  # 不能踢群主


class TestLeaveGroup:
    """测试退出群组"""

    def test_leave_group_success(self, client, db_session, app, sample_users):
        """测试成功退出群组"""
        with app.app_context():
            # 创建群组
            group = app.Conversation(
                type=2,
                name='Test Group',
                creator_id=sample_users[0]
            )
            app.db.session.add(group)
            app.db.session.flush()

            # 添加群主
            owner = app.ConversationMember(
                conversation_id=group.id,
                user_id=sample_users[0],
                role=2
            )
            app.db.session.add(owner)

            # 添加普通成员
            member = app.ConversationMember(
                conversation_id=group.id,
                user_id=sample_users[1],
                role=0
            )
            app.db.session.add(member)
            app.db.session.commit()

            # 使用普通成员token
            from flask_jwt_extended import create_access_token
            token = create_access_token(identity=str(sample_users[1]))
            headers = {'Authorization': f'Bearer {token}'}

            group_id = group.id

        resp = client.delete(f'/api/groups/{group_id}/members/me',
                            headers=headers)
        data = resp.get_json()

        assert resp.status_code == 200
        assert data['code'] == 0

    def test_leave_group_as_owner(self, client, db_session, app, sample_users):
        """测试群主退出群组"""
        with app.app_context():
            # 创建群组
            group = app.Conversation(
                type=2,
                name='Test Group',
                creator_id=sample_users[0]
            )
            app.db.session.add(group)
            app.db.session.flush()

            # 添加群主
            owner = app.ConversationMember(
                conversation_id=group.id,
                user_id=sample_users[0],
                role=2
            )
            app.db.session.add(owner)
            app.db.session.commit()

            # 使用群主token
            from flask_jwt_extended import create_access_token
            token = create_access_token(identity=str(sample_users[0]))
            headers = {'Authorization': f'Bearer {token}'}

            group_id = group.id

        resp = client.delete(f'/api/groups/{group_id}/members/me',
                            headers=headers)
        data = resp.get_json()

        assert resp.status_code == 200
        assert data['code'] == 1007  # 群主不能直接退出


class TestDismissGroup:
    """测试解散群组"""

    def test_dismiss_group_success(self, client, db_session, app, sample_users):
        """测试成功解散群组"""
        with app.app_context():
            # 创建群组
            group = app.Conversation(
                type=2,
                name='Test Group',
                creator_id=sample_users[0]
            )
            app.db.session.add(group)
            app.db.session.flush()

            # 添加群主
            owner = app.ConversationMember(
                conversation_id=group.id,
                user_id=sample_users[0],
                role=2
            )
            app.db.session.add(owner)

            # 添加普通成员
            member = app.ConversationMember(
                conversation_id=group.id,
                user_id=sample_users[1],
                role=0
            )
            app.db.session.add(member)
            app.db.session.commit()

            # 使用群主token
            from flask_jwt_extended import create_access_token
            token = create_access_token(identity=str(sample_users[0]))
            headers = {'Authorization': f'Bearer {token}'}

            group_id = group.id

        resp = client.delete(f'/api/groups/{group_id}',
                            headers=headers)
        data = resp.get_json()

        assert resp.status_code == 200
        assert data['code'] == 0

    def test_dismiss_group_no_permission(self, client, db_session, app, sample_users):
        """测试无权限解散群组"""
        with app.app_context():
            # 创建群组
            group = app.Conversation(
                type=2,
                name='Test Group',
                creator_id=sample_users[0]
            )
            app.db.session.add(group)
            app.db.session.flush()

            # 添加群主
            owner = app.ConversationMember(
                conversation_id=group.id,
                user_id=sample_users[0],
                role=2
            )
            app.db.session.add(owner)

            # 添加普通成员
            member = app.ConversationMember(
                conversation_id=group.id,
                user_id=sample_users[1],
                role=0
            )
            app.db.session.add(member)
            app.db.session.commit()

            # 使用普通成员token
            from flask_jwt_extended import create_access_token
            token = create_access_token(identity=str(sample_users[1]))
            headers = {'Authorization': f'Bearer {token}'}

            group_id = group.id

        resp = client.delete(f'/api/groups/{group_id}',
                            headers=headers)
        data = resp.get_json()

        assert resp.status_code == 200
        assert data['code'] == 1006
