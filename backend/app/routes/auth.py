# -*- coding: utf-8 -*-
"""
认证接口模块（成员A负责）
提供用户注册、登录、登出接口
"""
from flask import Blueprint, request

from app import db
from app.models.user import User
from app.services.auth_service import AuthService
from app.utils.auth import jwt_required_with_user
from app.utils.response import error, success
from app.utils.validators import validate_email, validate_password, validate_username

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    """用户注册"""
    data = request.get_json() or {}
    username = (data.get('username') or '').strip()
    password = data.get('password') or ''
    email = (data.get('email') or '').strip()
    nickname = (data.get('nickname') or '').strip()

    # 参数校验
    valid, msg = validate_username(username)
    if not valid:
        return error(1001, msg)
    valid, msg = validate_password(password)
    if not valid:
        return error(1001, msg)
    if email:
        valid, msg = validate_email(email)
        if not valid:
            return error(1001, msg)

    # 调用业务逻辑
    result = AuthService.register(username, password, email, nickname)
    if result['success']:
        return success(data=result['data'], message=result['message'])
    return error(result['code'], result['message'])


@auth_bp.route('/login', methods=['POST'])
def login():
    """用户登录"""
    data = request.get_json() or {}
    username = (data.get('username') or '').strip()
    password = data.get('password') or ''

    if not username or not password:
        return error(1001, '用户名和密码不能为空')

    result = AuthService.login(username, password)
    if result['success']:
        return success(data=result['data'], message=result['message'])
    return error(result['code'], result['message'])


@auth_bp.route('/logout', methods=['POST'])
@jwt_required_with_user
def logout(current_user_id):
    """用户登出"""
    return success(message='已登出')


@auth_bp.route('/me', methods=['GET'])
@jwt_required_with_user
def get_current_user(current_user_id):
    """获取当前登录用户信息"""
    user = User.query.get(current_user_id)
    if not user:
        return error(1007, '用户不存在')
    return success(data=user.to_dict(include_email=True))
