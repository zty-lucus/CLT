# -*- coding: utf-8 -*-
"""消息模型"""
from datetime import datetime

from app import db


class Message(db.Model):
    """消息表"""
    __tablename__ = 'messages'
    __table_args__ = (
        db.Index('idx_conv_created', 'conversation_id', 'created_at'),
    )

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversations.id', ondelete='CASCADE'),
                                nullable=False, index=True, comment='会话ID')
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'),
                          nullable=True, index=True, comment='发送者用户ID')
    msg_type = db.Column(db.SmallInteger, nullable=False, default=0,
                         comment='消息类型: 0=文本, 1=图片, 2=文件, 3=系统通知')
    content = db.Column(db.Text, nullable=True, default='', comment='消息内容')
    file_id = db.Column(db.Integer, db.ForeignKey('files.id', ondelete='SET NULL'),
                        nullable=True, comment='关联文件ID')
    status = db.Column(db.SmallInteger, nullable=False, default=0,
                       comment='状态: 0=已发送, 1=已送达, 2=已读')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, comment='发送时间')

    # 消息类型常量
    TYPE_TEXT = 0    # 文本
    TYPE_IMAGE = 1   # 图片
    TYPE_FILE = 2    # 文件
    TYPE_SYSTEM = 3  # 系统通知

    # 状态常量
    STATUS_SENT = 0       # 已发送
    STATUS_DELIVERED = 1  # 已送达
    STATUS_READ = 2       # 已读

    def to_dict(self):
        """转换为字典"""
        data = {
            'id': self.id,
            'conversation_id': self.conversation_id,
            'sender_id': self.sender_id,
            'msg_type': self.msg_type,
            'content': self.content or '',
            'file_id': self.file_id,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'sender': self.sender.to_dict() if self.sender else None,
        }
        if self.file:
            data['file'] = self.file.to_simple_dict()
        return data

    def __repr__(self):
        return f'<Message {self.id}: type={self.msg_type}>'
