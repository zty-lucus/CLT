# -*- coding: utf-8 -*-
"""
统一配置文件
包含数据库连接、JWT密钥、上传路径等所有配置项
"""
import os
from datetime import timedelta

# 项目根目录
BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


class Config:
    """基础配置"""
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY', 'campus-im-secret-key-change-in-production')

    # 数据库配置
    DB_USER = os.environ.get('DB_USER', 'root')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', '123456')
    DB_HOST = os.environ.get('DB_HOST', '127.0.0.1')
    DB_PORT = os.environ.get('DB_PORT', '3306')
    DB_NAME = os.environ.get('DB_NAME', 'campus_im')
    SQLALCHEMY_DATABASE_URI = (
        f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
        '?charset=utf8mb4'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 3600,
        'echo': False,
    }

    # JWT 配置
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

    # 文件上传配置
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
    ALLOWED_FILE_EXTENSIONS = {
        # 文档
        'doc', 'docx', 'pdf', 'txt', 'xls', 'xlsx', 'ppt', 'pptx',
        # 图片
        'jpg', 'jpeg', 'png', 'gif', 'bmp', 'svg', 'webp',
        # 压缩包
        'zip', 'rar', '7z', 'tar', 'gz',
        # 音视频
        'mp3', 'mp4', 'avi', 'mov', 'wav', 'flac',
        # 代码
        'py', 'js', 'html', 'css', 'java', 'c', 'cpp', 'h',
    }
    ALLOWED_FILE_MIME_TYPES = {
        'application/pdf',
        'text/plain',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'application/vnd.ms-excel',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'application/vnd.ms-powerpoint',
        'application/vnd.openxmlformats-officedocument.presentationml.presentation',
        'image/jpeg',
        'image/png',
        'image/gif',
        'image/bmp',
        'image/svg+xml',
        'image/webp',
        'application/zip',
        'application/x-rar-compressed',
        'application/x-7z-compressed',
        'application/x-tar',
        'application/gzip',
        'audio/mpeg',
        'audio/wav',
        'audio/flac',
        'video/mp4',
        'video/x-msvideo',
        'video/quicktime',
    }

    # CORS
    CORS_ORIGINS = ['http://localhost:5173', 'http://127.0.0.1:5173']


class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True


class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False


# 配置映射
config_map = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig,
}
