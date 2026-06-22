# -*- coding: utf-8 -*-
"""
用户业务逻辑（成员A负责）
"""
from app import db
from app.models.user import User
from app.utils.validators import validate_email


class UserService:
    """用户服务"""

    @staticmethod
    def update_profile(user_id, data):
        """更新用户资料"""
        user = User.query.get(user_id)
        if not user:
            return {'success': False, 'code': 1007, 'message': '用户不存在'}

        # 更新昵称
        if 'nickname' in data:
            nickname = (data['nickname'] or '').strip()
            if nickname:
                user.nickname = nickname

        # 更新头像
        if 'avatar' in data:
            user.avatar = data['avatar'] or ''

        # 更新邮箱
        if 'email' in data:
            email = (data['email'] or '').strip()
            if email:
                valid, msg = validate_email(email)
                if not valid:
                    return {'success': False, 'code': 1001, 'message': msg}
                # 检查邮箱是否已被其他人使用
                existing = User.query.filter(
                    User.email == email, User.id != user_id
                ).first()
                if existing:
                    return {'success': False, 'code': 1003, 'message': '邮箱已被使用'}
                user.email = email

        db.session.commit()
        return {
            'success': True,
            'message': '资料更新成功',
            'data': user.to_dict(include_email=True),
        }

    @staticmethod
    def search_users(keyword, current_user_id):
        """根据关键词搜索用户"""
        users = User.query.filter(
            User.id != current_user_id,
            db.or_(
                User.username.contains(keyword),
                User.nickname.contains(keyword),
                User.email.contains(keyword),
            ),
        ).limit(20).all()

        return [u.to_dict() for u in users]
