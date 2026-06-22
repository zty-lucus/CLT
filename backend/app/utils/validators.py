# -*- coding: utf-8 -*-
"""
参数校验工具
提供用户名、密码、邮箱等常见字段的格式校验
"""

import re


def validate_username(username):
    """
    校验用户名格式
    - 长度 4-20 字符
    - 仅允许字母、数字、下划线
    返回: (is_valid, error_message)
    """
    if not username or not isinstance(username, str):
        return False, '用户名不能为空'
    username = username.strip()
    if len(username) < 4 or len(username) > 20:
        return False, '用户名长度需在4-20字符之间'
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return False, '用户名仅允许字母、数字和下划线'
    return True, None


def validate_password(password):
    """
    校验密码强度
    - 长度至少8位
    - 必须包含字母和数字
    返回: (is_valid, error_message)
    """
    if not password or not isinstance(password, str):
        return False, '密码不能为空'
    if len(password) < 8:
        return False, '密码长度至少8位'
    if not re.search(r'[a-zA-Z]', password):
        return False, '密码必须包含字母'
    if not re.search(r'\d', password):
        return False, '密码必须包含数字'
    return True, None


def validate_email(email):
    """
    校验邮箱格式
    返回: (is_valid, error_message)
    """
    if not email or not isinstance(email, str):
        return False, '邮箱不能为空'
    email = email.strip()
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return False, '邮箱格式不正确'
    return True, None


def validate_file_size(file_size, max_size=50 * 1024 * 1024):
    """
    校验文件大小
    file_size: 文件大小（字节）
    max_size: 最大允许大小（字节），默认 50MB
    返回: (is_valid, error_message)
    """
    if file_size <= 0:
        return False, '文件大小无效'
    if file_size > max_size:
        max_mb = max_size / (1024 * 1024)
        return False, f'文件大小超过限制（最大{max_mb:.0f}MB）'
    return True, None


def validate_file_extension(filename, allowed_extensions=None):
    """
    校验文件扩展名
    返回: (is_valid, error_message)
    """
    if not filename or '.' not in filename:
        return False, '文件名无效'
    ext = filename.rsplit('.', 1)[1].lower()
    if allowed_extensions and ext not in allowed_extensions:
        return False, f'不支持的文件类型: .{ext}'
    return True, ext
