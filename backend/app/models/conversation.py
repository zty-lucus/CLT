# -*- coding: utf-8 -*-
"""会话与群组模型"""
from datetime import datetime

from app import db


class Conversation(db.Model):
    """会话表 - 支持单聊和群聊"""
    __tablename__ = 'conversations'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    type = db.Column(db.SmallInteger, nullable=False, default=0,
                     comment='会话类型: 0=单聊, 1=群聊')
    name = db.Column(db.String(100), nullable=True, default='', comment='会话名称（群聊使用）')
    avatar = db.Column(db.String(500), nullable=True, default='', comment='会话头像URL')
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'),
                           nullable=True, comment='创建者用户ID（群主）')
    announcement = db.Column(db.Text, nullable=True, default='', comment='群公告')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow,
                           onupdate=datetime.utcnow, comment='更新时间')

    # 会话类型常量
    TYPE_PRIVATE = 0  # 单聊
    TYPE_GROUP = 1    # 群聊

    # 关系
    messages = db.relationship('Message', backref='conversation', lazy='dynamic',
                               order_by='Message.created_at.desc()')
    members = db.relationship('ConversationMember', backref='conversation', lazy='dynamic')
    creator = db.relationship('User', foreign_keys=[creator_id], backref='created_conversations')

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'type': self.type,
            'name': self.name or '',
            'avatar': self.avatar or '',
            'creator_id': self.creator_id,
            'announcement': self.announcement or '',
            'member_count': self.members.count() if self.members else 0,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return f'<Conversation {self.id}: {self.name or "private"}>'


class ConversationMember(db.Model):
    """
    会话成员表
    记录用户与会话的多对多关系
    角色: 0=群主, 1=管理员, 2=普通成员
    """
    __tablename__ = 'conversation_members'
    __table_args__ = (
        db.UniqueConstraint('conversation_id', 'user_id', name='uq_conv_user'),
    )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversations.id', ondelete='CASCADE'),
                                nullable=False, index=True, comment='会话ID')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'),
                        nullable=False, index=True, comment='用户ID')
    role = db.Column(db.SmallInteger, nullable=False, default=2,
                     comment='角色: 0=群主, 1=管理员, 2=普通成员')
    joined_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, comment='加入时间')

    # 角色常量
    ROLE_OWNER = 0   # 群主
    ROLE_ADMIN = 1   # 管理员
    ROLE_MEMBER = 2  # 普通成员

    # 关系
    user = db.relationship('User', backref=db.backref('conversation_memberships', lazy='dynamic'))

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'conversation_id': self.conversation_id,
            'user_id': self.user_id,
            'role': self.role,
            'joined_at': self.joined_at.isoformat() if self.joined_at else None,
            'user': self.user.to_dict() if self.user else None,
        }

    def __repr__(self):
        return f'<ConversationMember {self.user_id} in {self.conversation_id}>'
