from datetime import datetime
from app.extensions import db


class Message(db.Model):
    __tablename__ = 'messages'

    id: int = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    conversation_id: int = db.Column(db.Integer, db.ForeignKey('conversations.id'), nullable=False)
    sender_id: int = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    msg_type: int = db.Column(db.SmallInteger, nullable=False, comment='1=text, 2=file, 3=image, 4=system')
    content: str = db.Column(db.Text, nullable=True)
    file_id: int = db.Column(db.Integer, db.ForeignKey('files.id'), nullable=True)
    status: int = db.Column(db.SmallInteger, default=0, comment='0=sent, 1=read')
    created_at: datetime = db.Column(db.DateTime, default=datetime.utcnow)

    file = db.relationship('File', foreign_keys=[file_id], backref='message')

    __table_args__ = (
        db.Index('ix_message_conversation_time', 'conversation_id', 'created_at'),
    )

    def __repr__(self) -> str:
        return f'<Message {self.id} conv={self.conversation_id} type={self.msg_type}>'
