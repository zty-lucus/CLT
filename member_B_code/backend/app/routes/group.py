"""
群组路由
依赖: services/group_service.py, utils/response.py
"""
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.services.group_service import GroupService
from app.utils.response import success, error

group_bp = Blueprint('group', __name__)


@group_bp.route('/api/groups', methods=['GET'])
@jwt_required()
def get_groups():
    """获取当前用户的群组列表"""
    user_id = get_jwt_identity()
    service = GroupService()
    groups = service.get_user_groups(user_id)
    return success(data=groups, message="获取群组列表成功")


@group_bp.route('/api/groups/<int:group_id>', methods=['GET'])
@jwt_required()
def get_group_detail(group_id):
    """获取群组详情"""
    user_id = get_jwt_identity()
    service = GroupService()
    detail = service.get_group_detail(group_id, user_id)
    if detail is None:
        return error(code=1007, message="群组不存在")
    return success(data=detail, message="获取群组详情成功")


@group_bp.route('/api/groups', methods=['POST'])
@jwt_required()
def create_group():
    """创建群组"""
    user_id = get_jwt_identity()
    data = request.get_json()
    name = data.get('name')
    member_ids = data.get('member_ids', [])
    if not name:
        return error(code=1001, message="缺少群组名称")
    service = GroupService()
    result = service.create_group(name, user_id, member_ids)
    return success(data=result, message="群组创建成功")


@group_bp.route('/api/groups/<int:group_id>', methods=['PUT'])
@jwt_required()
def update_group(group_id):
    """修改群信息（管理员/群主）"""
    user_id = get_jwt_identity()
    data = request.get_json()
    name = data.get('name')
    avatar = data.get('avatar')
    announcement = data.get('announcement')
    service = GroupService()
    result = service.update_group(group_id, user_id, name, avatar, announcement)
    if result is None:
        return error(code=1006, message="无权限修改群信息")
    return success(data=result, message="群信息修改成功")


@group_bp.route('/api/groups/<int:group_id>/members', methods=['GET'])
@jwt_required()
def get_group_members(group_id):
    """获取群成员列表"""
    user_id = get_jwt_identity()
    service = GroupService()
    result = service.get_group_members(group_id, user_id)
    if result is None:
        return error(code=1007, message="群组不存在或无权限")
    return success(data=result, message="获取群成员列表成功")


@group_bp.route('/api/groups/<int:group_id>/members', methods=['POST'])
@jwt_required()
def invite_member(group_id):
    """邀请成员加入群组"""
    user_id = get_jwt_identity()
    data = request.get_json()
    invitee_ids = data.get('user_ids', [])
    if not invitee_ids:
        return error(code=1001, message="缺少被邀请用户ID")
    service = GroupService()
    result = service.invite_members(group_id, user_id, invitee_ids)
    if result is None:
        return error(code=1006, message="无权限邀请成员")
    return success(data=result, message="成员邀请成功")


@group_bp.route('/api/groups/<int:group_id>/members/<int:target_id>', methods=['DELETE'])
@jwt_required()
def remove_member(group_id, target_id):
    """踢出群成员（管理员/群主）"""
    user_id = get_jwt_identity()
    service = GroupService()
    result = service.remove_member(group_id, user_id, target_id)
    if result is None:
        return error(code=1006, message="无权限移除群成员")
    return success(message="群成员已移除")


@group_bp.route('/api/groups/<int:group_id>/members/me', methods=['DELETE'])
@jwt_required()
def leave_group(group_id):
    """退出群组"""
    user_id = get_jwt_identity()
    service = GroupService()
    result = service.leave_group(group_id, user_id)
    if result is None:
        return error(code=1007, message="群组不存在或不在群中")
    return success(message="已退出群组")


@group_bp.route('/api/groups/<int:group_id>', methods=['DELETE'])
@jwt_required()
def dismiss_group(group_id):
    """解散群组（仅群主）"""
    user_id = get_jwt_identity()
    service = GroupService()
    result = service.dismiss_group(group_id, user_id)
    if result is None:
        return error(code=1006, message="仅群主可解散群组")
    return success(message="群组已解散")
