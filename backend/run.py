# -*- coding: utf-8 -*-
"""
应用启动入口
"""
import os

from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

from app import create_app
from app.extensions import socketio

config_name = os.environ.get('FLASK_ENV', 'development')
flask_app = create_app(config_name)

if __name__ == '__main__':
    # 使用socketio.run启动
    socketio.run(flask_app, host='0.0.0.0', port=5000, debug=False, use_reloader=False, log_output=True)
