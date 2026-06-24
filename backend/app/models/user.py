from datetime import datetime
from app.extensions import db


class User(db.Model):
    __tablename__ = 'users'

    id: int = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username: str = db.Column(db.String(50), unique=True, nullable=False)
    password_hash: str = db.Column(db.String(255), nullable=False)
    nickname: str = db.Column(db.String(50), nullable=True)
    avatar: str = db.Column(db.String(255), default='default.png')
    signature: str = db.Column(db.String(200), default='')
    email: str = db.Column(db.String(100), unique=True, nullable=True)
    status: int = db.Column(db.SmallInteger, default=0, comment='0=offline, 1=online')
    last_seen: datetime = db.Column(db.DateTime, nullable=True)
    created_at: datetime = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at: datetime = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # relationships
    sent_messages = db.relationship('Message', backref='sender', lazy='dynamic',
                                    foreign_keys='Message.sender_id')
    uploaded_files = db.relationship('File', backref='uploader', lazy='dynamic',
                                     foreign_keys='File.uploader_id')
    memberships = db.relationship('ConversationMember', backref='user', lazy='dynamic',
                                  foreign_keys='ConversationMember.user_id')

    def __repr__(self) -> str:
        return f'<User {self.id} {self.username}>'
