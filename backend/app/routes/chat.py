"""
会话与消息路由
依赖: services/message_service.py, utils/response.py
"""
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.services.message_service import MessageService
from app.utils.response import success, error

chat_bp = Blueprint('chat', __name__)


@chat_bp.route('/api/conversations', methods=['GET'])
@jwt_required()
def get_conversations():
    """获取当前用户的会话列表"""
    user_id = int(get_jwt_identity())
    service = MessageService()
    conversations = service.get_conversations(user_id)
    return success(data=conversations, message="获取会话列表成功")


@chat_bp.route('/api/conversations/<int:conv_id>', methods=['GET'])
@jwt_required()
def get_conversation_detail(conv_id):
    """获取会话详情"""
    user_id = int(get_jwt_identity())
    service = MessageService()
    detail = service.get_conversation_detail(conv_id, user_id)
    if detail is None:
        return error(code=1007, message="会话不存在")
    return success(data=detail, message="获取会话详情成功")


@chat_bp.route('/api/conversations/private', methods=['POST'])
@jwt_required()
def create_private_conversation():
    """创建单聊会话"""
    user_id = int(get_jwt_identity())
    data = request.get_json()
    target_id = data.get('target_id')
    if not target_id:
        return error(code=1001, message="缺少目标用户ID")
    service = MessageService()
    result = service.create_private_conversation(user_id, target_id)
    if result is None:
        return error(code=1007, message="目标用户不存在")
    return success(data=result, message="单聊会话创建成功")


@chat_bp.route('/api/conversations/group', methods=['POST'])
@jwt_required()
def create_group_conversation():
    """创建群聊会话（由群组服务创建后调用）"""
    user_id = int(get_jwt_identity())
    data = request.get_json()
    conversation_id = data.get('conversation_id')
    if not conversation_id:
        return error(code=1001, message="缺少会话ID")
    service = MessageService()
    result = service.get_conversation_detail(conversation_id, user_id)
    return success(data=result, message="群聊会话已就绪")


@chat_bp.route('/api/conversations/<int:conv_id>/messages', methods=['GET'])
@jwt_required()
def get_messages(conv_id):
    """获取历史消息（分页）"""
    user_id = int(get_jwt_identity())
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    service = MessageService()
    result = service.get_messages(conv_id, user_id, page, per_page)
    if result is None:
        return error(code=1007, message="会话不存在或无权限")
    return success(data=result, message="获取消息列表成功")


@chat_bp.route('/api/conversations/read', methods=['POST'])
@jwt_required()
def mark_conversation_read():
    """标记会话已读"""
    user_id = int(get_jwt_identity())
    data = request.get_json()
    conversation_id = data.get('conversation_id')
    if not conversation_id:
        return error(code=1001, message="缺少会话ID")
    service = MessageService()
    service.mark_read(conversation_id, user_id)
    return success(message="已标记已读")
