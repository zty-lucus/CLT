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
    created_at: datetime = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f'<File {self.id} {self.original_name}>'
