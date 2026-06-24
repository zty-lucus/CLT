from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services import user_service
from app.utils.response import success, error

user_bp = Blueprint('user', __name__)


@user_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    user_id = get_jwt_identity()
    result = user_service.get_profile(user_id)
    if result['code'] != 0:
        return error(result['code'], result['message'])
    return success(result['data'])


@user_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    user_id = get_jwt_identity()
    data = request.get_json(silent=True) or {}

    result = user_service.update_profile(
        user_id,
        username=data.get('username'),
        email=data.get('email'),
        nickname=data.get('nickname'),
        avatar=data.get('avatar'),
        signature=data.get('signature'),
    )
    if result['code'] != 0:
        return error(result['code'], result['message'])
    return success(result['data'], result['message'])
