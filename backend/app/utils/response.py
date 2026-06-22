# -*- coding: utf-8 -*-
"""
统一响应格式工具
所有 API 接口统一使用此模块返回数据
"""

from flask import jsonify


def success(data=None, message='操作成功'):
    """
    成功响应
    返回格式: {"code": 0, "message": "xxx", "data": {...}}
    """
    return jsonify({
        'code': 0,
        'message': message,
        'data': data,
    })


def error(code, message='操作失败', data=None):
    """
    错误响应
    返回格式: {"code": 1001, "message": "xxx", "data": null}

    统一错误码定义:
        0     - 成功
        1001  - 参数错误
        1002  - 用户名已存在
        1003  - 邮箱已存在
        1004  - 用户名或密码错误
        1005  - Token无效或过期
        1006  - 无权限
        1007  - 资源不存在
        1008  - 文件超大
        1009  - 文件类型不支持
        2001  - 已是好友
        2002  - 已在群组
    """
    return jsonify({
        'code': code,
        'message': message,
        'data': data,
    })


# 常用错误码常量
ERR_SUCCESS = 0
ERR_PARAM_ERROR = 1001
ERR_USERNAME_EXISTS = 1002
ERR_EMAIL_EXISTS = 1003
ERR_LOGIN_FAILED = 1004
ERR_TOKEN_INVALID = 1005
ERR_PERMISSION_DENIED = 1006
ERR_RESOURCE_NOT_FOUND = 1007
ERR_FILE_TOO_LARGE = 1008
ERR_FILE_TYPE_DENIED = 1009
ERR_ALREADY_FRIEND = 2001
ERR_ALREADY_IN_GROUP = 2002
