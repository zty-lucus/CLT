# -*- coding: utf-8 -*-
"""
Flask 应用工厂
创建并配置 Flask 应用实例，注册蓝图和扩展
"""
import os

from flask import Flask
from app.extensions import db, jwt, migrate, socketio, cors
from config import config_map


def create_app(config_name: str = 'default') -> Flask:
    """
    应用工厂函数
    config_name: 'development' | 'production' | 'testing' | 'default'
    """
    flask_app = Flask(__name__)

    # 加载配置
    flask_app.config.from_object(config_map.get(config_name, config_map['default']))

    # 确保上传目录存在
    os.makedirs(flask_app.config.get('UPLOAD_FOLDER', 'uploads'), exist_ok=True)

    # 初始化扩展
    db.init_app(flask_app)
    jwt.init_app(flask_app)
    migrate.init_app(flask_app, db)
    cors.init_app(flask_app, origins=flask_app.config.get('CORS_ORIGINS', ['*']), supports_credentials=True)
    socketio.init_app(flask_app, cors_allowed_origins='*')

    # 导入模型以便 Flask-Migrate 检测
    from app.models import User, Friendship, Conversation, ConversationMember, Message, File  # noqa: F401

    # 注册蓝图
    from app.routes.auth import auth_bp
    from app.routes.user import user_bp
    from app.routes.friend import friend_bp
    from app.routes.file import file_bp
    from app.routes.chat import chat_bp
    from app.routes.group import group_bp

    flask_app.register_blueprint(auth_bp, url_prefix='/api/auth')
    flask_app.register_blueprint(user_bp, url_prefix='/api/users')
    flask_app.register_blueprint(friend_bp, url_prefix='/api/friends')
    flask_app.register_blueprint(file_bp, url_prefix='/api/files')
    flask_app.register_blueprint(chat_bp)
    flask_app.register_blueprint(group_bp)

    # 注册 WebSocket 事件
    import app.sockets.connect_events  # noqa: F401
    import app.sockets.chat_events  # noqa: F401

    return flask_app
