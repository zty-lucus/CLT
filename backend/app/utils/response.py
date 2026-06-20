from typing import Any
from flask import jsonify


def success(data: Any = None, message: str = 'success') -> tuple:
    return jsonify({'code': 0, 'message': message, 'data': data}), 200


def error(code: int, message: str, status: int = 400) -> tuple:
    return jsonify({'code': code, 'message': message, 'data': None}), status
