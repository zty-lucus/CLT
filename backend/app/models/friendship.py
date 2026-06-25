from datetime import datetime
from app.extensions import db


class Friendship(db.Model):
    __tablename__ = 'friendships'

    STATUS_PENDING = 0
    STATUS_ACCEPTED = 1
    STATUS_REJECTED = 2
    STATUS_DELETED = 3

    id: int = db.Column(db.Integer, primary_key=True, autoincrement=True)
    requester_id: int = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    addressee_id: int = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status: int = db.Column(db.SmallInteger, default=0, comment='0=pending, 1=accepted, 2=rejected, 3=deleted')
    request_message: str = db.Column(db.String(200), default='')
    created_at: datetime = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at: datetime = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    requester = db.relationship('User', foreign_keys=[requester_id], backref='sent_requests')
    addressee = db.relationship('User', foreign_keys=[addressee_id], backref='received_requests')

    __table_args__ = (
        db.UniqueConstraint('requester_id', 'addressee_id', name='uq_friendship_pair'),
    )

    def to_dict(self, current_user_id=None):
        from app.models.user import User
        friend_id = self.addressee_id if self.requester_id == current_user_id else self.requester_id
        friend_user = db.session.get(User, friend_id)
        return {
            'id': self.id,
            'status': self.status,
            'request_message': self.request_message or '',
            'friend': {
                'id': friend_user.id if friend_user else None,
                'username': friend_user.username if friend_user else '',
                'nickname': friend_user.nickname if friend_user else '',
                'avatar': friend_user.avatar if friend_user else 'default.png',
                'status': friend_user.status if friend_user else 0,
            },
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else '',
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else '',
        }

    def __repr__(self) -> str:
        return f'<Friendship {self.requester_id}->{self.addressee_id} status={self.status}>'
