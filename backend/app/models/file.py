from datetime import datetime
from app.extensions import db


class File(db.Model):
    __tablename__ = 'files'

    id: int = db.Column(db.Integer, primary_key=True, autoincrement=True)
    uploader_id: int = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    original_name: str = db.Column(db.String(255), nullable=False)
    stored_name: str = db.Column(db.String(255), nullable=False)
    file_path: str = db.Column(db.String(500), nullable=False)
    file_size: int = db.Column(db.BigInteger, nullable=False)
    file_type: str = db.Column(db.String(50), nullable=True)
    mime_type: str = db.Column(db.String(100), nullable=True)
    md5_hash: str = db.Column(db.String(64), nullable=True)
    created_at: datetime = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'uploader_id': self.uploader_id,
            'original_name': self.original_name,
            'stored_name': self.stored_name,
            'file_path': self.file_path,
            'file_size': self.file_size,
            'file_type': self.file_type,
            'mime_type': self.mime_type or '',
            'md5_hash': self.md5_hash or '',
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else '',
        }

    def to_simple_dict(self):
        return {
            'id': self.id,
            'original_name': self.original_name,
            'file_size': self.file_size,
            'file_type': self.file_type,
            'mime_type': self.mime_type or '',
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else '',
        }

    def __repr__(self) -> str:
        return f'<File {self.id} {self.original_name}>'
