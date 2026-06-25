from datetime import datetime
from app.extensions import db


class Conversation(db.Model):
    __tablename__ = 'conversations'

    id: int = db.Column(db.Integer, primary_key=True, autoincrement=True)
    type: int = db.Column(db.SmallInteger, nullable=False, comment='1=private, 2=group')
    name: str = db.Column(db.String(100), nullable=True)
    avatar: str = db.Column(db.String(255), nullable=True)
    creator_id: int = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    announcement: str = db.Column(db.Text, nullable=True, default='')
    created_at: datetime = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at: datetime = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    creator = db.relationship('User', foreign_keys=[creator_id], backref='created_conversations')
    members = db.relationship('ConversationMember', backref='conversation', lazy='dynamic',
                              foreign_keys='ConversationMember.conversation_id')
    messages = db.relationship('Message', backref='conversation', lazy='dynamic',
                               foreign_keys='Message.conversation_id')

    def __repr__(self) -> str:
        return f'<Conversation {self.id} type={self.type}>'


class ConversationMember(db.Model):
    __tablename__ = 'conversation_members'

    id: int = db.Column(db.Integer, primary_key=True, autoincrement=True)
    conversation_id: int = db.Column(db.Integer, db.ForeignKey('conversations.id'), nullable=False)
    user_id: int = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    role: int = db.Column(db.SmallInteger, default=0, comment='0=member, 1=admin, 2=owner')
    unread_count: int = db.Column(db.Integer, default=0)
    joined_at: datetime = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('conversation_id', 'user_id', name='uq_conversation_member'),
    )

    def __repr__(self) -> str:
        return f'<ConversationMember conv={self.conversation_id} user={self.user_id}>'
