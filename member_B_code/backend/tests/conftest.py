# -*- coding: utf-8 -*-
"""
B分支测试配置
提供测试所需的fixture
"""
import pytest
import sys
import os

# 添加项目根目录到Python路径
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO
from flask_cors import CORS

# 创建扩展实例
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


# 创建app包结构
import types

# 创建app包
app_package = types.ModuleType('app')
app_package.__path__ = [os.path.join(backend_dir, 'app')]
app_package.db = db
app_package.User = User
app_package.Conversation = Conversation
app_package.ConversationMember = ConversationMember
app_package.Message = Message
app_package.socketio = socketio

# 注册app包
sys.modules['app'] = app_package

# 创建app.routes子包
routes_package = types.ModuleType('app.routes')
routes_package.__path__ = [os.path.join(backend_dir, 'app', 'routes')]
sys.modules['app.routes'] = routes_package

# 创建app.services子包
services_package = types.ModuleType('app.services')
services_package.__path__ = [os.path.join(backend_dir, 'app', 'services')]
sys.modules['app.services'] = services_package

# 创建app.sockets子包
sockets_package = types.ModuleType('app.sockets')
sockets_package.__path__ = [os.path.join(backend_dir, 'app', 'sockets')]
sys.modules['app.sockets'] = sockets_package

# 创建app.utils子包
utils_package = types.ModuleType('app.utils')
utils_package.__path__ = [os.path.join(backend_dir, 'app', 'utils')]
sys.modules['app.utils'] = utils_package

# 创建app.models子包
models_package = types.ModuleType('app.models')
models_package.User = User
models_package.Conversation = Conversation
models_package.ConversationMember = ConversationMember
models_package.Message = Message
sys.modules['app.models'] = models_package


@pytest.fixture(scope='session')
def app():
    """创建测试应用"""
    flask_app = Flask(__name__)
    flask_app.config['TESTING'] = True
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    flask_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    flask_app.config['JWT_SECRET_KEY'] = 'test-secret-key'
    flask_app.config['SECRET_KEY'] = 'test-secret'

    # 初始化扩展
    db.init_app(flask_app)
    jwt.init_app(flask_app)
    CORS(flask_app)
    socketio.init_app(flask_app, cors_allowed_origins='*')

    with flask_app.app_context():
        # 创建所有表
        db.create_all()

        # 存储模型到app以便测试使用
        flask_app.User = User
        flask_app.Conversation = Conversation
        flask_app.ConversationMember = ConversationMember
        flask_app.Message = Message
        flask_app.db = db

        # 注册蓝图
        from app.routes.chat import chat_bp
        from app.routes.group import group_bp

        flask_app.register_blueprint(chat_bp)
        flask_app.register_blueprint(group_bp)

        yield flask_app

        db.drop_all()


@pytest.fixture(scope='function')
def client(app):
    """创建测试客户端"""
    return app.test_client()


@pytest.fixture(scope='function')
def db_session(app):
    """数据库fixture，每个测试后清理数据"""
    with app.app_context():
        yield db
        # 清理所有表数据
        for table in reversed(db.metadata.sorted_tables):
            db.session.execute(table.delete())
        db.session.commit()


@pytest.fixture
def sample_user(app, db_session):
    """创建示例用户"""
    with app.app_context():
        user = User(
            username='testuser',
            nickname='Test User',
            avatar='https://example.com/avatar.jpg'
        )
        db.session.add(user)
        db.session.commit()
        # 返回用户ID而不是对象，避免DetachedInstanceError
        return user.id


@pytest.fixture
def sample_users(app, db_session):
    """创建多个示例用户"""
    with app.app_context():
        user_ids = []
        for i in range(3):
            user = User(
                username=f'user{i}',
                nickname=f'User {i}',
                avatar=f'https://example.com/avatar{i}.jpg'
            )
            db.session.add(user)
            db.session.flush()
            user_ids.append(user.id)
        db.session.commit()
        return user_ids


@pytest.fixture
def sample_conversation(app, db_session, sample_user):
    """创建示例会话"""
    with app.app_context():
        conv = Conversation(
            type=1,
            name='',
            creator_id=sample_user
        )
        db.session.add(conv)
        db.session.flush()

        # 添加成员
        member = ConversationMember(
            conversation_id=conv.id,
            user_id=sample_user,
            role=0
        )
        db.session.add(member)
        db.session.commit()
        return conv.id


@pytest.fixture
def sample_group(app, db_session, sample_users):
    """创建示例群组"""
    with app.app_context():
        group = Conversation(
            type=2,
            name='Test Group',
            creator_id=sample_users[0],
            announcement='Test announcement'
        )
        db.session.add(group)
        db.session.flush()

        # 添加群主
        owner_member = ConversationMember(
            conversation_id=group.id,
            user_id=sample_users[0],
            role=2
        )
        db.session.add(owner_member)

        # 添加普通成员
        for user_id in sample_users[1:]:
            member = ConversationMember(
                conversation_id=group.id,
                user_id=user_id,
                role=0
            )
            db.session.add(member)

        db.session.commit()
        return group.id


@pytest.fixture
def auth_headers(app, client, db_session, sample_user):
    """创建认证headers"""
    from flask_jwt_extended import create_access_token
    with app.app_context():
        token = create_access_token(identity=str(sample_user))
        return {'Authorization': f'Bearer {token}'}
