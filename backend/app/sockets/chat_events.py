"""
核心聊天 WebSocket 事件处理
依赖: services/message_service.py, utils/auth.py
"""
from flask import request
from flask_socketio import emit, join_room

from app import socketio
from app.services.message_service import MessageService
from app.utils.auth import verify_token_from_socket


@socketio.on('send_message')
def handle_send_message(data):
    """处理客户端发送消息事件"""
    token = data.get('token', '')
    user_id = verify_token_from_socket(token)
    if user_id is None:
        emit('error', {'message': '认证失败'})
        return

    conversation_id = data.get('conversation_id')
    msg_type = data.get('msg_type', 1)
    content = data.get('content', '')
    file_id = data.get('file_id')

    if not conversation_id or (msg_type == 1 and not content.strip()):
        emit('error', {'message': '消息内容不能为空'})
        return

    service = MessageService()
    saved_msg = service.save_message(
        sender_id=user_id,
        conversation_id=conversation_id,
        msg_type=msg_type,
        content=content,
        file_id=file_id,
    )

    # 获取会话成员列表
    member_ids = service.get_member_ids(conversation_id)

    # 向会话房间内所有成员推送新消息
    for mid in member_ids:
        room_name = f'user_{mid}'
        emit(
            'new_message',
            saved_msg,
            room=room_name,
            include_self=False,
        )

    # 返回确认给发送者
    emit('new_message', saved_msg, room=f'user_{user_id}')


@socketio.on('msg_read')
def handle_msg_read(data):
    """处理标记已读事件"""
    token = data.get('token', '')
    user_id = verify_token_from_socket(token)
    if user_id is None:
        return

    conversation_id = data.get('conversation_id')
    if not conversation_id:
        return

    service = MessageService()
    service.mark_read(conversation_id, user_id)


@socketio.on('typing')
def handle_typing(data):
    """处理正在输入事件"""
    token = data.get('token', '')
    user_id = verify_token_from_socket(token)
    if user_id is None:
        return

    conversation_id = data.get('conversation_id')
    if not conversation_id:
        return

    service = MessageService()
    member_ids = service.get_member_ids(conversation_id)

    for mid in member_ids:
        if mid != user_id:
            emit(
                'user_typing',
                {'conversation_id': conversation_id, 'user_id': user_id},
                room=f'user_{mid}',
            )


@socketio.on('join_conversation')
def handle_join_conversation(data):
    """客户端加入会话房间"""
    token = data.get('token', '')
    user_id = verify_token_from_socket(token)
    if user_id is None:
        return

    conversation_id = data.get('conversation_id')
    if conversation_id:
        join_room(f'user_{user_id}')
