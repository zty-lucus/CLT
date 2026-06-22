# -*- coding: utf-8 -*-
"""
聊天 WebSocket 事件处理（成员B负责）
处理消息发送、接收、已读等实时通信事件
"""
from app import db, socketio


@socketio.on('send_message')
def handle_send_message(data):
    """处理客户端发送消息事件"""
    # TODO: 成员B实现
    pass


@socketio.on('msg_read')
def handle_msg_read(data):
    """处理消息已读事件"""
    # TODO: 成员B实现
    pass
