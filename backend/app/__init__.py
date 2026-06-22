# -*- coding: utf-8 -*-
"""
Flask 应用工厂
创建并配置 Flask 应用实例，注册蓝图和扩展
"""
import os

from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy

# 初始化扩展（不绑定应用）
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
socketio = SocketIO(cors_allowed_origins='*', async_mode='eventlet')


def create_app(config_name=None):
    """
    应用工厂函数
    config_name: 'development' | 'production' | 'default'
    """
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')

    app = Flask(__name__)

    # 加载配置
    from app.config import config_map
    app.config.from_object(config_map.get(config_name, config_map['default']))

    # 确保上传目录存在
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # 初始化扩展
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    CORS(app, origins=app.config.get('CORS_ORIGINS', ['*']), supports_credentials=True)
    socketio.init_app(app, cors_allowed_origins='*')

    # 注册蓝图
    from app.routes.auth import auth_bp
    from app.routes.user import user_bp
    from app.routes.friend import friend_bp
    from app.routes.file import file_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(user_bp, url_prefix='/api/user')
    app.register_blueprint(friend_bp, url_prefix='/api/friends')
    app.register_blueprint(file_bp, url_prefix='/api/files')

    # 注册 WebSocket 事件
    with app.app_context():
        from app.sockets import connect_events  # noqa: F401

    return app
