# -*- coding: utf-8 -*-
"""
应用启动入口
"""
import os

from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

from app import create_app, socketio  # noqa: E402

config_name = os.environ.get('FLASK_ENV', 'development')
app = create_app(config_name)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
