# -*- coding: utf-8 -*-
"""
文件接口模块（成员C负责）
提供文件上传、下载、信息查询、删除等 REST API
"""
import os

from flask import Blueprint, current_app, request, send_file
from flask_jwt_extended import decode_token

from app.services.file_service import FileService
from app.utils.auth import jwt_required_with_user
from app.utils.response import error, success

file_bp = Blueprint('file', __name__)


def _get_user_id_from_request():
    """从请求中获取用户ID，支持 Authorization header 和 query param token"""
    from flask_jwt_extended import verify_jwt_in_request
    try:
        verify_jwt_in_request()
        from flask_jwt_extended import get_jwt_identity
        return int(get_jwt_identity())
    except Exception:
        pass
    # 尝试从 query param 获取
    token = request.args.get('token')
    if token:
        try:
            payload = decode_token(token)
            return int(payload.get('sub'))
        except Exception:
            pass
    return None


# ============================================================
# 文件上传
# ============================================================

@file_bp.route('/upload', methods=['POST'])
@jwt_required_with_user
def upload_file(current_user_id):
    """
    上传文件
    POST /api/files/upload
    FormData: file=文件
    返回文件元数据
    """
    if 'file' not in request.files:
        return error(1001, '请选择要上传的文件')

    file_obj = request.files['file']

    # 先做基本校验并获取文件信息
    is_valid, code, msg, file_info = FileService.validate_file(file_obj)
    if not is_valid:
        return error(code, msg)

    # 保存文件
    is_success, code, msg, file_record = FileService.save_upload(file_obj, current_user_id)
    if not is_success:
        return error(code, msg)

    return success(
        data=file_record.to_simple_dict(),
        message=f'文件上传成功（{FileService._format_size(file_record.file_size)}）',
    )


@file_bp.route('/upload/multiple', methods=['POST'])
@jwt_required_with_user
def upload_multiple_files(current_user_id):
    """
    批量上传文件
    POST /api/files/upload/multiple
    FormData: files=多个文件
    """
    if 'files' not in request.files:
        return error(1001, '请选择要上传的文件')

    files = request.files.getlist('files')
    if not files:
        return error(1001, '请选择要上传的文件')

    max_batch = 10
    if len(files) > max_batch:
        return error(1001, f'单次最多上传{max_batch}个文件')

    results = []
    errors = []
    for file_obj in files:
        is_success, code, msg, file_record = FileService.save_upload(file_obj, current_user_id)
        if is_success:
            results.append(file_record.to_simple_dict())
        else:
            errors.append({'filename': file_obj.filename, 'error': msg})

    return success(data={
        'uploaded': results,
        'failed': errors,
        'success_count': len(results),
        'failed_count': len(errors),
    })


# ============================================================
# 文件下载
# ============================================================

@file_bp.route('/<int:file_id>/download', methods=['GET'])
def download_file(file_id):
    """
    下载文件
    GET /api/files/123/download
    支持 ?inline=1 参数用于浏览器内预览
    支持 ?token=xxx 参数用于认证（兼容 window.open）
    """
    current_user_id = _get_user_id_from_request()
    if current_user_id is None:
        return error(1005, 'Token无效或已过期')

    file_record, file_path = FileService.get_file_path(file_id, current_user_id)
    if not file_record:
        return error(1007, '文件不存在')
    if not file_path:
        return error(1007, '文件已被删除或损坏')

    # 是否内联显示（预览），默认作为附件下载
    as_inline = request.args.get('inline', '0') == '1'
    download_name = file_record.original_name

    try:
        return send_file(
            file_path,
            as_attachment=not as_inline,
            download_name=download_name,
            mimetype=file_record.mime_type or 'application/octet-stream',
        )
    except Exception as e:
        return error(1007, f'文件读取失败: {str(e)}')


# ============================================================
# 文件信息查询
# ============================================================

@file_bp.route('/<int:file_id>', methods=['GET'])
@jwt_required_with_user
def get_file_info(current_user_id, file_id):
    """
    获取文件详情
    GET /api/files/123
    """
    result = FileService.get_file_info(file_id, current_user_id)
    if result['success']:
        return success(data=result['data'])
    return error(result['code'], result['message'])


@file_bp.route('/my', methods=['GET'])
@jwt_required_with_user
def get_my_files(current_user_id):
    """
    获取我的文件列表（分页）
    GET /api/files/my?page=1&per_page=20
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    # 限制每页最大数量
    per_page = min(per_page, 50)

    result = FileService.get_user_files(current_user_id, page, per_page)
    return success(data=result)


# ============================================================
# 文件删除
# ============================================================

@file_bp.route('/<int:file_id>', methods=['DELETE'])
@jwt_required_with_user
def delete_file(current_user_id, file_id):
    """
    删除文件
    DELETE /api/files/123
    """
    result = FileService.delete_file(file_id, current_user_id)
    if result['success']:
        return success(message=result['message'])
    return error(result['code'], result['message'])


# ============================================================
# 辅助函数
# ============================================================

def _format_size(size_bytes):
    """将字节数格式化为可读的文件大小字符串"""
    if size_bytes < 1024:
        return f'{size_bytes}B'
    elif size_bytes < 1024 * 1024:
        return f'{size_bytes / 1024:.1f}KB'
    elif size_bytes < 1024 * 1024 * 1024:
        return f'{size_bytes / (1024 * 1024):.1f}MB'
    else:
        return f'{size_bytes / (1024 * 1024 * 1024):.2f}GB'


# Monkey-patch 工具方法到 FileService
FileService._format_size = staticmethod(_format_size)
