from app.extensions import db
from app.models.user import User


def get_profile(user_id: int) -> dict:
    user = db.session.get(User, user_id)
    if not user:
        return {'code': 1007, 'message': '用户不存在'}

    return {
        'code': 0,
        'message': 'success',
        'data': {
            'id': user.id,
            'username': user.username,
            'nickname': user.nickname,
            'avatar': user.avatar,
            'signature': user.signature,
            'email': user.email,
            'status': user.status,
            'created_at': user.created_at.strftime('%Y-%m-%d %H:%M:%S') if user.created_at else None,
        }
    }


def update_profile(user_id: int, **kwargs) -> dict:
    user = db.session.get(User, user_id)
    if not user:
        return {'code': 1007, 'message': '用户不存在'}

    username = kwargs.get('username')
    email = kwargs.get('email')
    nickname = kwargs.get('nickname')
    avatar = kwargs.get('avatar')
    signature = kwargs.get('signature')

    if username and username != user.username:
        if User.query.filter_by(username=username).first():
            return {'code': 1002, 'message': '用户名已存在'}
        user.username = username

    if email and email != user.email:
        if User.query.filter_by(email=email).first():
            return {'code': 1003, 'message': '邮箱已存在'}
        user.email = email

    if nickname is not None:
        user.nickname = nickname
    if avatar is not None:
        user.avatar = avatar
    if signature is not None:
        user.signature = signature

    db.session.commit()

    return {
        'code': 0,
        'message': '更新成功',
        'data': {
            'id': user.id,
            'username': user.username,
            'nickname': user.nickname,
            'avatar': user.avatar,
            'signature': user.signature,
            'email': user.email,
        }
    }
