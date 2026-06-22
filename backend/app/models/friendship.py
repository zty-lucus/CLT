# -*- coding: utf-8 -*-
"""好友关系模型"""
from datetime import datetime

from app import db


class Friendship(db.Model):
    """
    好友关系表
    状态: 0=待同意, 1=已同意, 2=已拒绝, 3=已删除
    """
    __tablename__ = 'friendships'
    __table_args__ = (
        db.UniqueConstraint('requester_id', 'addressee_id', name='uq_requester_addressee'),
    )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    requester_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'),
                             nullable=False, index=True, comment='发起方用户ID')
    addressee_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'),
                             nullable=False, index=True, comment='接收方用户ID')
    status = db.Column(db.SmallInteger, nullable=False, default=0,
                       comment='状态: 0=待同意, 1=已同意, 2=已拒绝, 3=已删除')
    request_message = db.Column(db.String(200), nullable=True, default='', comment='验证消息')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, comment='请求时间')
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow,
                           onupdate=datetime.utcnow, comment='更新时间')

    # 关系
    requester = db.relationship('User', foreign_keys=[requester_id],
                                backref=db.backref('sent_friend_requests', lazy='dynamic'))
    addressee = db.relationship('User', foreign_keys=[addressee_id],
                                backref=db.backref('received_friend_requests', lazy='dynamic'))

    # 状态常量
    STATUS_PENDING = 0   # 待同意
    STATUS_ACCEPTED = 1  # 已同意
    STATUS_REJECTED = 2  # 已拒绝
    STATUS_DELETED = 3   # 已删除

    def to_dict(self, current_user_id=None):
        """转换为字典，current_user_id用于确定对方信息"""
        data = {
            'id': self.id,
            'requester_id': self.requester_id,
            'addressee_id': self.addressee_id,
            'status': self.status,
            'request_message': self.request_message or '',
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

        # 如果提供了current_user_id，返回对方的信息
        if current_user_id is not None:
            if self.requester_id == current_user_id:
                data['friend'] = self.addressee.to_dict() if self.addressee else None
            else:
                data['friend'] = self.requester.to_dict() if self.requester else None

        return data

    def __repr__(self):
        return f'<Friendship {self.requester_id} -> {self.addressee_id} ({self.status})>'
