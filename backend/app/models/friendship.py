from datetime import datetime
from app.extensions import db


class Friendship(db.Model):
    __tablename__ = 'friendships'

    id: int = db.Column(db.Integer, primary_key=True, autoincrement=True)
    requester_id: int = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    addressee_id: int = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status: int = db.Column(db.SmallInteger, default=0, comment='0=pending, 1=accepted, 2=rejected')
    created_at: datetime = db.Column(db.DateTime, default=datetime.utcnow)

    requester = db.relationship('User', foreign_keys=[requester_id], backref='sent_requests')
    addressee = db.relationship('User', foreign_keys=[addressee_id], backref='received_requests')

    __table_args__ = (
        db.UniqueConstraint('requester_id', 'addressee_id', name='uq_friendship_pair'),
    )

    def __repr__(self) -> str:
        return f'<Friendship {self.requester_id}->{self.addressee_id} status={self.status}>'
