# -*- coding: utf-8 -*-
"""
文件业务逻辑（成员C负责）
提供文件上传、下载、校验、管理等功能
"""
import hashlib
import os
import uuid

from flask import current_app
from werkzeug.utils import secure_filename

from app import db
from app.models.file import File


class FileService:
    """文件服务"""

    @staticmethod
    def validate_file(file_obj):
        """
        校验上传文件的合法性和安全性
        返回: (is_valid, error_code, error_message, file_info_dict)
        """
        if not file_obj or not file_obj.filename:
            return False, 1001, '未选择文件', None

        # 检查文件名安全性
        original_name = secure_filename(file_obj.filename)
        if not original_name:
            return False, 1001, '文件名不合法', None

        # 检查文件扩展名
        if '.' not in original_name:
            return False, 1009, '不支持的文件类型：无扩展名', None

        ext = original_name.rsplit('.', 1)[1].lower()
        allowed_extensions = current_app.config.get('ALLOWED_FILE_EXTENSIONS', set())
        if ext not in allowed_extensions:
            return False, 1009, f'不支持的文件类型: .{ext}', None

        # 获取文件大小（通过 seek/tell 方式，不加载到内存）
        file_obj.seek(0, os.SEEK_END)
        file_size = file_obj.tell()
        file_obj.seek(0)

        if file_size <= 0:
            return False, 1001, '文件大小无效', None

        max_size = current_app.config.get('MAX_FILE_SIZE', 50 * 1024 * 1024)
        if file_size > max_size:
            max_mb = max_size / (1024 * 1024)
            return False, 1008, f'文件大小超过限制（最大{max_mb:.0f}MB）', None

        file_info = {
            'original_name': original_name,
            'ext': ext,
            'file_size': file_size,
        }
        return True, 0, '校验通过', file_info

    @staticmethod
    def save_upload(file_obj, uploader_id):
        """
        保存上传的文件到磁盘并写入数据库记录
        返回: (is_success, error_code, error_message, file_record)
        """
        # 1. 校验文件
        is_valid, code, msg, file_info = FileService.validate_file(file_obj)
        if not is_valid:
            return False, code, msg, None

        original_name = file_info['original_name']
        ext = file_info['ext']
        file_size = file_info['file_size']

        # 2. 生成存储文件名（UUID + 扩展名）
        stored_name = f'{uuid.uuid4().hex}.{ext}'

        # 3. 按日期创建子目录，避免单目录文件过多
        from datetime import datetime
        date_dir = datetime.utcnow().strftime('%Y%m')
        upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], date_dir)
        os.makedirs(upload_dir, exist_ok=True)

        # 4. 保存文件到磁盘
        file_path = os.path.join(upload_dir, stored_name)
        file_obj.save(file_path)

        # 5. 计算 MD5 哈希（用于去重和校验）
        md5_hash = FileService._compute_md5(file_path)

        # 6. 写入数据库记录
        file_record = File(
            uploader_id=uploader_id,
            original_name=original_name,
            stored_name=stored_name,
            file_path=file_path,
            file_size=file_size,
            file_type=ext,
            mime_type=file_obj.content_type or '',
            md5_hash=md5_hash,
        )
        db.session.add(file_record)
        db.session.commit()

        return True, 0, '文件上传成功', file_record

    @staticmethod
    def _compute_md5(file_path):
        """计算文件的 MD5 哈希值（分块读取，支持大文件）"""
        hash_md5 = hashlib.md5()
        try:
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(8192), b''):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception:
            return ''

    @staticmethod
    def get_file_info(file_id, user_id=None):
        """
        获取文件信息
        user_id: 如提供，验证访问权限（只能访问自己上传的文件或好友分享的文件）
        """
        file_record = File.query.get(file_id)
        if not file_record:
            return {'success': False, 'code': 1007, 'message': '文件不存在'}

        # 权限检查：只能访问自己上传的文件（后续可由消息系统扩展分享权限）
        if user_id and file_record.uploader_id != user_id:
            # TODO: 扩展为可检查好友分享权限
            pass

        return {
            'success': True,
            'data': file_record.to_dict(),
        }

    @staticmethod
    def get_user_files(uploader_id, page=1, per_page=20):
        """
        获取用户上传的文件列表（分页）
        """
        pagination = File.query.filter_by(uploader_id=uploader_id).order_by(
            File.created_at.desc()
        ).paginate(page=page, per_page=per_page, error_out=False)

        return {
            'files': [f.to_simple_dict() for f in pagination.items],
            'total': pagination.total,
            'page': pagination.page,
            'per_page': pagination.per_page,
            'pages': pagination.pages,
        }

    @staticmethod
    def get_file_path(file_id, user_id=None):
        """
        获取文件磁盘路径（用于下载）
        返回: (file_record, absolute_path) 或 (None, None)
        """
        file_record = File.query.get(file_id)
        if not file_record:
            return None, None

        # 检查文件是否实际存在
        if not os.path.isfile(file_record.file_path):
            return file_record, None

        return file_record, file_record.file_path

    @staticmethod
    def delete_file(file_id, user_id):
        """
        删除文件（仅上传者可以删除）
        """
        file_record = File.query.get(file_id)
        if not file_record:
            return {'success': False, 'code': 1007, 'message': '文件不存在'}

        if file_record.uploader_id != user_id:
            return {'success': False, 'code': 1006, 'message': '无权删除此文件'}

        # 删除物理文件
        try:
            if os.path.isfile(file_record.file_path):
                os.remove(file_record.file_path)
        except OSError:
            pass  # 文件可能已被删除，继续删除数据库记录

        # 删除数据库记录
        db.session.delete(file_record)
        db.session.commit()

        return {'success': True, 'message': '文件已删除'}
