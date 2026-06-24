from datetime import datetime
from flask import request
from flask_socketio import emit
from flask_jwt_extended import decode_token
from app.extensions import db, socketio
from app.models.user import User


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
        user_id = payload['sub']
    except Exception:
        return False

    user = db.session.get(User, int(user_id))
    if not user:
        return False

    user.status = 1
    user.last_seen = datetime.utcnow()
    db.session.commit()

    from flask_socketio import join_room
    join_room(f'user_{user.id}')

    emit('user_online', {'user_id': user.id, 'username': user.username}, broadcast=True)


@socketio.on('disconnect')
def handle_disconnect():
    user_id = _get_user_id_from_session()
    if not user_id:
        return

    user = db.session.get(User, user_id)
    if user:
        user.status = 0
        user.last_seen = datetime.utcnow()
        db.session.commit()

    emit('user_offline', {'user_id': user_id}, broadcast=True)


def _get_user_id_from_session():
    try:
        token = request.args.get('token')
        if token:
            payload = decode_token(token)
            return int(payload['sub'])
    except Exception:
        pass
    return None
