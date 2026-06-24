# -*- coding: utf-8 -*-
"""
测试用Flask应用
用于独立测试B分支代码
"""
import os
import sys

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO
from flask_cors import CORS

# 初始化扩展
db = SQLAlchemy()
jwt = JWTManager()
socketio = SocketIO(cors_allowed_origins='*', async_mode='eventlet')


# 定义模型
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    nickname = db.Column(db.String(80))
    avatar = db.Column(db.String(200))
    status = db.Column(db.Integer, default=0)


class Conversation(db.Model):
    __tablename__ = 'conversations'
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.Integer, nullable=False)  # 1:单聊 2:群聊
    name = db.Column(db.String(100))
    avatar = db.Column(db.String(200))
    creator_id = db.Column(db.Integer)
    announcement = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())


class ConversationMember(db.Model):
    __tablename__ = 'conversation_members'
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversations.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    role = db.Column(db.Integer, default=0)  # 0:普通成员 1:管理员 2:群主
    unread_count = db.Column(db.Integer, default=0)
    joined_at = db.Column(db.DateTime, default=db.func.now())


class Message(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversations.id'), nullable=False)
    sender_id = db.Column(db.Integer, nullable=False)
    msg_type = db.Column(db.Integer, default=1)  # 1:文本 2:文件 3:图片 4:系统
    content = db.Column(db.Text)
    file_id = db.Column(db.Integer)
    status = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=db.func.now())


# 模拟app模块中的导入
class MockApp:
    """模拟app模块"""
    db = db
    User = User
    Conversation = Conversation
    ConversationMember = ConversationMember
    Message = Message
    socketio = socketio


def create_test_app():
    """创建测试应用"""
    # 设置模拟的app模块
    mock_app = MockApp()
    sys.modules['app'] = mock_app
    sys.modules['app.models'] = type('Module', (), {
        'User': User,
        'Conversation': Conversation,
        'ConversationMember': ConversationMember,
        'Message': Message
    })()

    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = 'test-secret-key'
    app.config['SECRET_KEY'] = 'test-secret'

    # 初始化扩展
    db.init_app(app)
    jwt.init_app(app)
    CORS(app)
    socketio.init_app(app, cors_allowed_origins='*')

    with app.app_context():
        # 创建所有表
        db.create_all()

        # 存储模型到app以便测试使用
        app.User = User
        app.Conversation = Conversation
        app.ConversationMember = ConversationMember
        app.Message = Message
        app.db = db

        # 注册蓝图
        from app.routes.chat import chat_bp
        from app.routes.group import group_bp

        app.register_blueprint(chat_bp)
        app.register_blueprint(group_bp)

        # 注册WebSocket事件
        from app.sockets import chat_events

        return app


if __name__ == '__main__':
    app = create_test_app()
    socketio.run(app, host='0.0.0.0', port=5001, debug=True)
