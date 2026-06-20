from flask import Flask
from app.extensions import db, jwt, migrate, socketio, cors
from config import config_map


def create_app(config_name: str = 'default') -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_map[config_name])

    # init extensions
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app)
    socketio.init_app(app, cors_allowed_origins='*')

    # import models so Flask-Migrate can detect them
    from app.models import User, Friendship, Conversation, ConversationMember, Message, File  # noqa: F401

    # register socket events
    import app.sockets.connect_events  # noqa: F401

    # register blueprints
    from app.routes.auth import auth_bp
    from app.routes.user import user_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(user_bp, url_prefix='/api/users')

    return app
