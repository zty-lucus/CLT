from functools import wraps
from flask import request
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from app.utils.response import error


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


def get_current_user_id() -> int:
    """获取当前登录用户ID"""
    return get_jwt_identity()
