from datetime import datetime
from flask import request
from flask_socketio import emit, join_room
from flask_jwt_extended import decode_token
from app.extensions import db, socketio
from app.models.user import User

# 存储 sid -> user_id 的映射，用于 disconnect 时获取用户信息
_sid_user_map = {}


@socketio.on('connect')
def handle_connect(auth):
    token = None
    if isinstance(auth, dict):
        token = auth.get('token')
    if not token:
        token = request.args.get('token')
    if not token:
        return False

    try:
        payload = decode_token(token)
        user_id = int(payload['sub'])
    except Exception:
        return False

    user = db.session.get(User, user_id)
    if not user:
        return False

    user.status = 1
    user.last_seen = datetime.utcnow()
    db.session.commit()

    # 记录 sid -> user_id 映射
    _sid_user_map[request.sid] = user_id

    join_room(f'user_{user.id}')

    emit('user_online', {'user_id': user.id, 'username': user.username}, broadcast=True)


@socketio.on('disconnect')
def handle_disconnect():
    user_id = _sid_user_map.pop(request.sid, None)
    if not user_id:
        return

    user = db.session.get(User, user_id)
    if user:
        user.status = 0
        user.last_seen = datetime.utcnow()
        db.session.commit()

    emit('user_offline', {'user_id': user_id}, broadcast=True)
