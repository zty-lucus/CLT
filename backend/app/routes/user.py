# -*- coding: utf-8 -*-
"""
用户接口模块（成员A负责）
提供用户信息查询、修改接口
"""
from flask import Blueprint, request

from app import db
from app.models.user import User
from app.services.user_service import UserService
from app.utils.auth import jwt_required_with_user
from app.utils.response import error, success

user_bp = Blueprint('user', __name__)


@user_bp.route('/profile', methods=['GET'])
@jwt_required_with_user
def get_profile(current_user_id):
    """获取个人信息"""
    user = User.query.get(current_user_id)
    if not user:
        return error(1007, '用户不存在')
    return success(data=user.to_dict(include_email=True))


@user_bp.route('/profile', methods=['PUT'])
@jwt_required_with_user
def update_profile(current_user_id):
    """更新个人信息（昵称、头像、邮箱）"""
    data = request.get_json() or {}
    result = UserService.update_profile(current_user_id, data)
    if result['success']:
        return success(data=result['data'], message=result['message'])
    return error(result['code'], result['message'])


@user_bp.route('/search', methods=['GET'])
@jwt_required_with_user
def search_users(current_user_id):
    """搜索用户"""
    keyword = (request.args.get('keyword') or '').strip()
    if not keyword:
        return error(1001, '搜索关键词不能为空')

    users = UserService.search_users(keyword, current_user_id)
    return success(data={'users': users, 'total': len(users)})
