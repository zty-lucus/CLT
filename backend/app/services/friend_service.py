# -*- coding: utf-8 -*-
"""
好友业务逻辑（成员C负责）
提供好友添加、搜索、请求处理、删除等核心业务
"""
from app import db
from app.models.user import User
from app.models.friendship import Friendship


class FriendService:
    """好友服务"""

    @staticmethod
    def search_users(keyword, current_user_id):
        """
        搜索可添加的用户
        排除自己、已有好友、已有待处理请求的用户
        """
        # 获取与当前用户有好友关系的用户ID列表
        friend_ids_query = db.session.query(Friendship.addressee_id).filter(
            Friendship.requester_id == current_user_id,
            Friendship.status.in_([Friendship.STATUS_PENDING, Friendship.STATUS_ACCEPTED]),
        ).union(
            db.session.query(Friendship.requester_id).filter(
                Friendship.addressee_id == current_user_id,
                Friendship.status.in_([Friendship.STATUS_PENDING, Friendship.STATUS_ACCEPTED]),
            )
        ).all()
        friend_ids = {row[0] for row in friend_ids_query}
        friend_ids.add(current_user_id)

        # 搜索用户
        users = User.query.filter(
            User.id.notin_(friend_ids),
            db.or_(
                User.username.contains(keyword),
                User.nickname.contains(keyword),
            ),
        ).limit(20).all()

        return [u.to_dict() for u in users]

    @staticmethod
    def send_request(requester_id, addressee_id, message=''):
        """
        发送好友申请
        """
        # 不能添加自己
        if requester_id == addressee_id:
            return {'success': False, 'code': 1001, 'message': '不能添加自己为好友'}

        # 检查目标用户是否存在
        addressee = User.query.get(addressee_id)
        if not addressee:
            return {'success': False, 'code': 1007, 'message': '用户不存在'}

        # 检查是否已存在好友关系
        existing = Friendship.query.filter(
            db.or_(
                db.and_(
                    Friendship.requester_id == requester_id,
                    Friendship.addressee_id == addressee_id,
                ),
                db.and_(
                    Friendship.requester_id == addressee_id,
                    Friendship.addressee_id == requester_id,
                ),
            ),
            Friendship.status.in_([Friendship.STATUS_PENDING, Friendship.STATUS_ACCEPTED]),
        ).first()

        if existing:
            if existing.status == Friendship.STATUS_PENDING:
                if existing.requester_id == requester_id:
                    return {'success': False, 'code': 2001, 'message': '已发送过好友申请，请等待对方处理'}
                else:
                    # 对方已经发过申请，自动接受
                    existing.status = Friendship.STATUS_ACCEPTED
                    db.session.commit()
                    return {
                        'success': True,
                        'message': '已自动成为好友',
                        'data': existing.to_dict(current_user_id=requester_id),
                    }
            elif existing.status == Friendship.STATUS_ACCEPTED:
                return {'success': False, 'code': 2001, 'message': '已经是好友'}

        # 创建好友申请
        friendship = Friendship(
            requester_id=requester_id,
            addressee_id=addressee_id,
            status=Friendship.STATUS_PENDING,
            request_message=message or '',
        )
        db.session.add(friendship)
        db.session.commit()

        return {
            'success': True,
            'message': '好友申请已发送',
            'data': friendship.to_dict(current_user_id=requester_id),
        }

    @staticmethod
    def accept_request(friendship_id, current_user_id):
        """
        同意好友申请
        只有接收方可以同意
        """
        friendship = Friendship.query.get(friendship_id)
        if not friendship:
            return {'success': False, 'code': 1007, 'message': '好友申请不存在'}

        if friendship.addressee_id != current_user_id:
            return {'success': False, 'code': 1006, 'message': '无权处理此申请'}

        if friendship.status != Friendship.STATUS_PENDING:
            return {'success': False, 'code': 1001, 'message': '该申请已处理'}

        friendship.status = Friendship.STATUS_ACCEPTED
        db.session.commit()

        return {
            'success': True,
            'message': '已添加为好友',
            'data': friendship.to_dict(current_user_id=current_user_id),
        }

    @staticmethod
    def reject_request(friendship_id, current_user_id):
        """
        拒绝好友申请
        只有接收方可以拒绝
        """
        friendship = Friendship.query.get(friendship_id)
        if not friendship:
            return {'success': False, 'code': 1007, 'message': '好友申请不存在'}

        if friendship.addressee_id != current_user_id:
            return {'success': False, 'code': 1006, 'message': '无权处理此申请'}

        if friendship.status != Friendship.STATUS_PENDING:
            return {'success': False, 'code': 1001, 'message': '该申请已处理'}

        friendship.status = Friendship.STATUS_REJECTED
        db.session.commit()

        return {
            'success': True,
            'message': '已拒绝好友申请',
        }

    @staticmethod
    def delete_friend(friendship_id, current_user_id):
        """
        删除好友关系
        双方都可以删除
        """
        friendship = Friendship.query.get(friendship_id)
        if not friendship:
            return {'success': False, 'code': 1007, 'message': '好友关系不存在'}

        if current_user_id not in (friendship.requester_id, friendship.addressee_id):
            return {'success': False, 'code': 1006, 'message': '无权删除此关系'}

        if friendship.status != Friendship.STATUS_ACCEPTED:
            return {'success': False, 'code': 1001, 'message': '不是好友关系，无法删除'}

        friendship.status = Friendship.STATUS_DELETED
        db.session.commit()

        return {
            'success': True,
            'message': '已删除好友',
        }

    @staticmethod
    def get_friend_list(current_user_id):
        """
        获取好友列表
        返回所有已接受的好友关系
        """
        friendships = Friendship.query.filter(
            db.or_(
                Friendship.requester_id == current_user_id,
                Friendship.addressee_id == current_user_id,
            ),
            Friendship.status == Friendship.STATUS_ACCEPTED,
        ).order_by(Friendship.updated_at.desc()).all()

        friend_list = []
        for f in friendships:
            friend_data = f.to_dict(current_user_id=current_user_id)
            friend_list.append(friend_data)

        return friend_list

    @staticmethod
    def get_pending_requests(current_user_id):
        """
        获取待处理的好友申请
        分为：我发出的（sent）和 我收到的（received）
        """
        # 我发出的待处理申请
        sent = Friendship.query.filter(
            Friendship.requester_id == current_user_id,
            Friendship.status == Friendship.STATUS_PENDING,
        ).order_by(Friendship.created_at.desc()).all()

        # 我收到的待处理申请
        received = Friendship.query.filter(
            Friendship.addressee_id == current_user_id,
            Friendship.status == Friendship.STATUS_PENDING,
        ).order_by(Friendship.created_at.desc()).all()

        return {
            'sent': [f.to_dict(current_user_id=current_user_id) for f in sent],
            'received': [f.to_dict(current_user_id=current_user_id) for f in received],
        }

    @staticmethod
    def get_friend_detail(friendship_id, current_user_id):
        """
        获取好友详情
        """
        friendship = Friendship.query.get(friendship_id)
        if not friendship:
            return {'success': False, 'code': 1007, 'message': '好友关系不存在'}

        if current_user_id not in (friendship.requester_id, friendship.addressee_id):
            return {'success': False, 'code': 1006, 'message': '无权查看'}

        return {
            'success': True,
            'data': friendship.to_dict(current_user_id=current_user_id),
        }
