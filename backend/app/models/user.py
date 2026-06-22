# -*- coding: utf-8 -*-
"""用户模型"""
from datetime import datetime

from app import db


class User(db.Model):
    """用户表"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True, comment='用户名')
    password_hash = db.Column(db.String(255), nullable=False, comment='密码哈希')
    nickname = db.Column(db.String(50), nullable=True, default='', comment='昵称')
    avatar = db.Column(db.String(500), nullable=True, default='', comment='头像URL')
    email = db.Column(db.String(100), unique=True, nullable=True, comment='邮箱')
    status = db.Column(db.SmallInteger, nullable=False, default=0, comment='在线状态: 0=离线, 1=在线')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, comment='注册时间')
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow,
                           onupdate=datetime.utcnow, comment='更新时间')

    # 关系
    sent_messages = db.relationship('Message', foreign_keys='Message.sender_id',
                                    backref='sender', lazy='dynamic')
    uploaded_files = db.relationship('File', backref='uploader', lazy='dynamic')

    def to_dict(self, include_email=False):
        """转换为字典"""
        data = {
            'id': self.id,
            'username': self.username,
            'nickname': self.nickname or self.username,
            'avatar': self.avatar or '',
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
        if include_email:
            data['email'] = self.email
        return data

    def __repr__(self):
        return f'<User {self.id}: {self.username}>'
