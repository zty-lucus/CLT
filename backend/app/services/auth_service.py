from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from app.extensions import db
from app.models.user import User
from app.utils.validators import validate_username, validate_password, validate_email


def register(username: str, password: str, email: str, nickname: str) -> dict:
    ok, msg = validate_username(username)
    if not ok:
        return {'code': 1001, 'message': msg}

    ok, msg = validate_password(password)
    if not ok:
        return {'code': 1001, 'message': msg}

    ok, msg = validate_email(email)
    if not ok:
        return {'code': 1001, 'message': msg}

    if User.query.filter_by(username=username).first():
        return {'code': 1002, 'message': '用户名已存在'}

    if email and User.query.filter_by(email=email).first():
        return {'code': 1003, 'message': '邮箱已存在'}

    user = User(
        username=username,
        password_hash=generate_password_hash(password),
        email=email,
        nickname=nickname or username,
    )
    db.session.add(user)
    db.session.commit()

    return {'code': 0, 'message': '注册成功', 'data': {'user_id': user.id}}


def login(username: str, password: str) -> dict:
    if not username or not password:
        return {'code': 1001, 'message': '用户名和密码不能为空'}

    user = User.query.filter_by(username=username).first()
    if not user or not check_password_hash(user.password_hash, password):
        return {'code': 1004, 'message': '用户名或密码错误'}

    token = create_access_token(identity=user.id)

    return {
        'code': 0,
        'message': '登录成功',
        'data': {
            'token': token,
            'user': {
                'id': user.id,
                'username': user.username,
                'nickname': user.nickname,
                'avatar': user.avatar,
            }
        }
    }
