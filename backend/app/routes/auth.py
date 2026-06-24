from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from app.services import auth_service
from app.utils.response import success, error
from app.utils.auth import get_current_user_id

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json(silent=True) or {}
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    email = data.get('email', '').strip() or None
    nickname = data.get('nickname', '').strip() or None

    result = auth_service.register(username, password, email, nickname)
    if result['code'] != 0:
        return error(result['code'], result['message'])
    return success(result['data'], result['message'])


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json(silent=True) or {}
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()

    result = auth_service.login(username, password)
    if result['code'] != 0:
        return error(result['code'], result['message'])
    return success(result['data'], result['message'])


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    return success(message='登出成功')
