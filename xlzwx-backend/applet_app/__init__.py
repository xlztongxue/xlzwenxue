import os
import sys
from flask import Flask, request, abort, g, jsonify
from lib.flask_logging import enable_logging
from flask_cors import CORS

from models import db
from lib import redis_utils
from lib.jwt_utils import verify_jwt

def create_applet_app(config=None):
    """
    创建Flask app 的工厂函数
    :param config:
    :return:
    """
    app = Flask(__name__)
    if config is None:
        raise ValueError('config is None.')
    app.config.from_object(config)
    # 允许跨域
    CORS(app)

    # 注册sqlalchemy
    register_db(app)

    if not app.debug:
        enable_logging(app)

    # 注册蓝图
    register_blueprints(app)

    # 注册redis
    register_redis(app)

    # 注册请求钩子
    register_hooks(app)

    @app.route('/all_route')
    def all_route():
        data = {}
        for i in app.url_map.iter_rules():
            data[i.endpoint] = i.rule
        return jsonify(data)

    return app


def register_db(app):
    db.init_app(app)
    db.app = app


def register_blueprints(app):
    from applet_app import test
    app.register_blueprint(test.bp)
    from applet_app import user
    app.register_blueprint(user.bp, url_prefix='/user')
    from applet_app import mybooks
    app.register_blueprint(mybooks.bp, url_prefix='/mybooks')
    from applet_app import category
    app.register_blueprint(category.bp, url_prefix='/categorys')
    from applet_app import search
    app.register_blueprint(search.bp, url_prefix='/search')
    from applet_app import recommend
    app.register_blueprint(recommend.bp, url_prefix='/recommended')
    from applet_app import my
    app.register_blueprint(my.bp, url_prefix='/my')
    from applet_app import book
    app.register_blueprint(book.bp, url_prefix='/book')
    from applet_app import reader_config
    app.register_blueprint(reader_config.bp, url_prefix='/config')


def register_redis(app):
    redis_utils.init_app(app)


def register_hooks(app):
    @app.before_request
    def before_request():
        """
        在进入视图函数处理前先获取用户信息
        :return:
        """
        g.user_id = None
        authorization = request.headers.get('Authorization')
        print(authorization)
        payload = verify_jwt(authorization)
        print(payload)
        if payload:
            g.user_id = payload['user_id']


