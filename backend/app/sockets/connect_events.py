# -*- coding: utf-8 -*-
"""
WebSocket 连接/断开事件处理（成员A负责基础，成员C扩展）
"""
from flask import request

from app import db, socketio
from app.models.user import User


@socketio.on('connect')
def handle_connect():
    """客户端连接事件"""
    token = request.args.get('token')
    if not token:
        # 允许连接但不认证，后续可由具体事件验证
        return True

    try:
        from flask_jwt_extended import decode_token
        decoded = decode_token(token)
        user_id = int(decoded.get('sub'))
        user = User.query.get(user_id)
        if user:
            user.status = 1
            db.session.commit()
            # 广播用户上线
            socketio.emit('user_online', {'user_id': user_id})
    except Exception:
        pass


@socketio.on('disconnect')
def handle_disconnect():
    """客户端断开连接事件"""
    token = request.args.get('token')
    if not token:
        return

    try:
        from flask_jwt_extended import decode_token
        decoded = decode_token(token)
        user_id = int(decoded.get('sub'))
        user = User.query.get(user_id)
        if user:
            user.status = 0
            db.session.commit()
            # 广播用户离线
            socketio.emit('user_offline', {'user_id': user_id})
    except Exception:
        pass
