# -*- coding: utf-8 -*-
"""
JWT 认证工具
提供 Token 创建、验证、用户获取等辅助函数
"""

from functools import wraps

from flask import current_app
from flask import request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    verify_jwt_in_request,
)
from werkzeug.security import generate_password_hash, check_password_hash

from app.utils.response import error, ERR_TOKEN_INVALID


def hash_password(password):
    """对密码进行哈希加密"""
    return generate_password_hash(password)


def verify_password(password, password_hash):
    """验证密码是否匹配"""
    return check_password_hash(password_hash, password)


def generate_token(user_id):
    """
    生成 JWT Token
    返回 access_token 和 refresh_token
    """
    access_token = create_access_token(identity=str(user_id))
    refresh_token = create_refresh_token(identity=str(user_id))
    return {
        'access_token': access_token,
        'refresh_token': refresh_token,
    }


def get_current_user_id():
    """
    从当前请求的 JWT Token 中获取用户ID
    需在 jwt_required 之后调用
    """
    identity = get_jwt_identity()
    if identity is None:
        return None
    return int(identity)


def verify_token_from_socket(token):
    """
    从WebSocket token中验证并获取用户ID
    用于WebSocket事件认证
    """
    try:
        from flask_jwt_extended import decode_token
        decoded = decode_token(token)
        user_id = int(decoded.get('sub'))
        return user_id
    except Exception:
        return None


def jwt_required_optional():
    """装饰器：JWT验证，失败返回统一错误格式"""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                verify_jwt_in_request()
            except Exception:
                return error(1005, 'Token无效或过期', 401)
            return fn(*args, **kwargs)
        return wrapper
    return decorator


def jwt_required_with_user(fn):
    """
    带 JWT 验证的装饰器
    验证通过后将 current_user_id 注入到被装饰函数的参数中
    """

    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
            user_id = get_current_user_id()
            if user_id is None:
                return error(ERR_TOKEN_INVALID, 'Token无效或已过期')
        except Exception:
            return error(ERR_TOKEN_INVALID, 'Token无效或已过期')
        return fn(current_user_id=user_id, *args, **kwargs)

    return wrapper
