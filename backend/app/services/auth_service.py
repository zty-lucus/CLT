# -*- coding: utf-8 -*-
"""
认证业务逻辑（成员A负责）
"""
from app import db
from app.models.user import User
from app.utils.auth import generate_token, hash_password, verify_password


class AuthService:
    """认证服务"""

    @staticmethod
    def register(username, password, email='', nickname=''):
        """用户注册"""
        # 检查用户名是否存在
        if User.query.filter_by(username=username).first():
            return {'success': False, 'code': 1002, 'message': '用户名已存在'}

        # 检查邮箱是否存在
        if email and User.query.filter_by(email=email).first():
            return {'success': False, 'code': 1003, 'message': '邮箱已存在'}

        # 创建用户
        user = User(
            username=username,
            password_hash=hash_password(password),
            email=email or None,
            nickname=nickname or username,
        )
        db.session.add(user)
        db.session.commit()

        # 生成 Token
        tokens = generate_token(user.id)
        return {
            'success': True,
            'message': '注册成功',
            'data': {
                'user': user.to_dict(include_email=True),
                **tokens,
            },
        }

    @staticmethod
    def login(username, password):
        """用户登录"""
        # 查找用户（支持用户名或邮箱登录）
        user = User.query.filter(
            db.or_(User.username == username, User.email == username)
        ).first()

        if not user:
            return {'success': False, 'code': 1004, 'message': '用户名或密码错误'}

        if not verify_password(password, user.password_hash):
            return {'success': False, 'code': 1004, 'message': '用户名或密码错误'}

        # 更新在线状态
        user.status = 1
        db.session.commit()

        # 生成 Token
        tokens = generate_token(user.id)
        return {
            'success': True,
            'message': '登录成功',
            'data': {
                'user': user.to_dict(include_email=True),
                **tokens,
            },
        }
