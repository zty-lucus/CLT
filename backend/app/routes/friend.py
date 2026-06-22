# -*- coding: utf-8 -*-
"""
好友接口模块（成员C负责）
提供好友搜索、申请、同意、拒绝、删除、列表等 REST API
"""
from flask import Blueprint, request

from app.services.friend_service import FriendService
from app.utils.auth import jwt_required_with_user
from app.utils.response import error, success

friend_bp = Blueprint('friend', __name__)


# ============================================================
# 好友搜索与申请
# ============================================================

@friend_bp.route('/search', methods=['GET'])
@jwt_required_with_user
def search_users(current_user_id):
    """
    搜索可添加的用户
    GET /api/friends/search?keyword=xxx
    """
    keyword = (request.args.get('keyword') or '').strip()
    if not keyword:
        return error(1001, '搜索关键词不能为空')
    if len(keyword) < 2:
        return error(1001, '搜索关键词至少2个字符')

    users = FriendService.search_users(keyword, current_user_id)
    return success(data={'users': users, 'total': len(users)})


@friend_bp.route('/request', methods=['POST'])
@jwt_required_with_user
def send_friend_request(current_user_id):
    """
    发送好友申请
    POST /api/friends/request
    Body: { "addressee_id": 123, "message": "你好，我是xxx" }
    """
    data = request.get_json() or {}
    addressee_id = data.get('addressee_id')
    message = (data.get('message') or '').strip()

    if not addressee_id:
        return error(1001, '请指定要添加的用户')

    result = FriendService.send_request(current_user_id, addressee_id, message)
    if result['success']:
        return success(data=result.get('data'), message=result['message'])
    return error(result['code'], result['message'])


# ============================================================
# 好友申请处理
# ============================================================

@friend_bp.route('/request/<int:friendship_id>/accept', methods=['POST'])
@jwt_required_with_user
def accept_friend_request(current_user_id, friendship_id):
    """
    同意好友申请
    POST /api/friends/request/123/accept
    """
    result = FriendService.accept_request(friendship_id, current_user_id)
    if result['success']:
        return success(data=result.get('data'), message=result['message'])
    return error(result['code'], result['message'])


@friend_bp.route('/request/<int:friendship_id>/reject', methods=['POST'])
@jwt_required_with_user
def reject_friend_request(current_user_id, friendship_id):
    """
    拒绝好友申请
    POST /api/friends/request/123/reject
    """
    result = FriendService.reject_request(friendship_id, current_user_id)
    if result['success']:
        return success(message=result['message'])
    return error(result['code'], result['message'])


# ============================================================
# 好友列表与详情
# ============================================================

@friend_bp.route('/list', methods=['GET'])
@jwt_required_with_user
def get_friend_list(current_user_id):
    """
    获取好友列表
    GET /api/friends/list
    """
    friends = FriendService.get_friend_list(current_user_id)
    return success(data={'friends': friends, 'total': len(friends)})


@friend_bp.route('/requests', methods=['GET'])
@jwt_required_with_user
def get_pending_requests(current_user_id):
    """
    获取待处理的好友申请
    GET /api/friends/requests
    """
    result = FriendService.get_pending_requests(current_user_id)
    return success(data=result)


@friend_bp.route('/<int:friendship_id>', methods=['GET'])
@jwt_required_with_user
def get_friend_detail(current_user_id, friendship_id):
    """
    获取好友关系详情
    GET /api/friends/123
    """
    result = FriendService.get_friend_detail(friendship_id, current_user_id)
    if result['success']:
        return success(data=result['data'])
    return error(result['code'], result['message'])


# ============================================================
# 好友删除
# ============================================================

@friend_bp.route('/<int:friendship_id>', methods=['DELETE'])
@jwt_required_with_user
def delete_friend(current_user_id, friendship_id):
    """
    删除好友
    DELETE /api/friends/123
    """
    result = FriendService.delete_friend(friendship_id, current_user_id)
    if result['success']:
        return success(message=result['message'])
    return error(result['code'], result['message'])
