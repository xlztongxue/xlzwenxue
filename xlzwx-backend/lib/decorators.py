from functools import wraps
from flask import g, jsonify


def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not g.user_id:
            return jsonify({'msg': '缺少token或token已过期'}), 401
        return func(*args, **kwargs)
    return wrapper


def api_login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not g.user_id:
            return {'msg': '缺少token或token已过期'}, 401
        return func(*args, **kwargs)

    return wrapper