# -*- coding: utf-8 -*-
"""文件模型"""
from datetime import datetime

from app import db


class File(db.Model):
    """文件表 - 存储上传文件的元数据"""
    __tablename__ = 'files'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    uploader_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'),
                            nullable=False, index=True, comment='上传者用户ID')
    original_name = db.Column(db.String(500), nullable=False, comment='原始文件名')
    stored_name = db.Column(db.String(500), nullable=False, comment='存储文件名（UUID）')
    file_path = db.Column(db.String(1000), nullable=False, comment='文件存储路径')
    file_size = db.Column(db.BigInteger, nullable=False, default=0, comment='文件大小（字节）')
    file_type = db.Column(db.String(50), nullable=False, default='', comment='文件类型/扩展名')
    mime_type = db.Column(db.String(100), nullable=True, default='', comment='MIME类型')
    md5_hash = db.Column(db.String(64), nullable=True, default='', comment='MD5哈希值，用于去重')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, comment='上传时间')

    # 关系
    messages = db.relationship('Message', backref='file', lazy='dynamic')

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'uploader_id': self.uploader_id,
            'original_name': self.original_name,
            'stored_name': self.stored_name,
            'file_size': self.file_size,
            'file_type': self.file_type,
            'mime_type': self.mime_type or '',
            'md5_hash': self.md5_hash or '',
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'uploader': self.uploader.to_dict() if self.uploader else None,
        }

    def to_simple_dict(self):
        """简化为字典（不含uploader详细信息）"""
        return {
            'id': self.id,
            'uploader_id': self.uploader_id,
            'original_name': self.original_name,
            'file_size': self.file_size,
            'file_type': self.file_type,
            'mime_type': self.mime_type or '',
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f'<File {self.id}: {self.original_name}>'
