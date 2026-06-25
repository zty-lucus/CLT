import os
from datetime import timedelta

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

    # MySQL
    DB_USER = os.environ.get('DB_USER', 'root')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', 'REMOVED')
    DB_HOST = os.environ.get('DB_HOST', '127.0.0.1')
    DB_PORT = os.environ.get('DB_PORT', '3306')
    DB_NAME = os.environ.get('DB_NAME', 'campus_im')
    SQLALCHEMY_DATABASE_URI = (
        f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
        '?charset=utf8mb4'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 3600,
    }

    # JWT
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

    # Upload
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB
    MAX_FILE_SIZE = 50 * 1024 * 1024
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    ALLOWED_FILE_EXTENSIONS = {
        'doc', 'docx', 'pdf', 'txt', 'xls', 'xlsx', 'ppt', 'pptx',
        'jpg', 'jpeg', 'png', 'gif', 'bmp', 'svg', 'webp',
        'zip', 'rar', '7z', 'tar', 'gz',
        'mp3', 'mp4', 'avi', 'mov', 'wav', 'flac',
        'py', 'js', 'html', 'css', 'java', 'c', 'cpp', 'h',
    }
    ALLOWED_FILE_MIME_TYPES = {
        'application/pdf', 'text/plain',
        'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'application/vnd.ms-powerpoint', 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
        'image/jpeg', 'image/png', 'image/gif', 'image/bmp', 'image/svg+xml', 'image/webp',
        'application/zip', 'application/x-rar-compressed', 'application/x-7z-compressed',
        'application/x-tar', 'application/gzip',
        'audio/mpeg', 'audio/wav', 'audio/flac',
        'video/mp4', 'video/x-msvideo', 'video/quicktime',
    }

    # CORS
    CORS_ORIGINS = [
        'http://localhost:3000', 'http://127.0.0.1:3000',
        'http://localhost:3003', 'http://127.0.0.1:3003',
        'http://localhost:5173', 'http://127.0.0.1:5173',
    ]


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = False


class ProductionConfig(Config):
    DEBUG = False


config_map = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig,
}
