from flask import Blueprint, request, current_app, jsonify
import json
from datetime import datetime, timedelta
import random

from lib import wxauth
from lib import redis_utils
from lib.jwt_utils import generate_jwt
from models import User, db
from models import Book, BookShelf

bp = Blueprint('user', __name__)


def _add_book_shelf(user_id, sex):
    """书架增加默认书籍"""
    books = Book.query.filter(Book.showed == 1).all()
    choice_books = random.sample(books, 5)
    for book in choice_books:
        db.session.add(BookShelf(book_id=book.book_id,
                                 user_id=user_id,
                                 book_name=book.book_name,
                                 cover=book.cover))
    db.session.commit()


def _generate_tokens(user_id):
    """
    生成token 和refresh_token
    :param user_id: 用户id
    :return: token, refresh_token
    """
    # 颁发JWT
    now = datetime.utcnow()
    expiry = now + timedelta(hours=current_app.config['JWT_EXPIRY_HOURS'])
    token = generate_jwt({'user_id': user_id}, expiry)
    return token


@bp.route('/login', methods=['POST'])
def login():
    """ 第三方登录 """
    # code 用户登录凭证（有效期五分钟）。开发者需要在开发者服务器后台调用 auth.code2Session，
    # 使用 code 换取 openid 和 session_key 等信息
    code = request.json.get('code', '')
    # iv 加密算法的初始向量
    iv = request.json.get('iv', '')
    # encryptedData 包括敏感数据在内的完整用户信息的加密数据
    encryptedData = request.json.get('encryptedData', '')

    if not iv or not encryptedData or not code:
        return jsonify(msg='参数有误'), 403
    data = wxauth.get_wxapp_session_key(code)
    print('data', data)
    if 'session_key' not in data:
        return jsonify(msg='获取session_key失败', data=data), 500
    user_info = wxauth.get_user_info(encryptedData, iv, data['session_key'])
    if 'openId' not in user_info:
        return jsonify(msg='获取用户信息失败', user_info=user_info), 403

    user = User.query.filter_by(openId=user_info.get('openId')).first()
    if not user:
        user = User(user_info)
        db.session.add(user)
        db.session.flush()
        # 书架增加随机书籍
        _add_book_shelf(user.id, user.gender)
    else:
        # 更新用户信息
        user.update_info(user_info)
        db.session.commit()
    # 生成jwt token
    token = _generate_tokens(user.id)

    ret_data = {
        "token": token,
        "userInfo": {
            "uid": user.id,
            "gender": user.gender,
            "avatarUrl": user.avatarUrl
        },
        "config": {
            "preference": user.preference,
            "brightness": user.brightness,
            "fontSize": user.fontSize,
            "background": user.background,
            "turn": user.turn
        }
    }
    return jsonify(ret_data)


@bp.route('/tmp_add_user', methods=['POST'])
def tmp_add_user():
    """
    添加测试用户
    :return:
    """
    data = dict(
        openId='1'*32,
        nickName='测试用户002',
        gender=1,
        city='广州市',
        province='广东省',
        country='中国',
        avatarUrl='default'
    )
    user = User(data)
    db.session.add(user)
    db.session.flush()
    _add_book_shelf(user.id, user.gender)
    ret_data = {
        'msg': '添加成功',
        'user_id': user.id,
    }
    return jsonify(ret_data)


@bp.route('/tmp_login')
def tmp_login():
    """
    登录测试接口
    :return:
    """
    user_id = request.args.get('user_id')
    user = User.query.get(user_id)

    # 生成jwt token
    token = _generate_tokens(user_id)

    ret_data = {
        "token": token,
        "userInfo": {
            "uid": user.id,
            "gender": user.gender,
            "avatarUrl": user.avatarUrl
        },
        "config": {
            "preference": user.preference,
            "brightness": user.brightness,
            "fontSize": user.fontSize,
            "background": user.background,
            "turn": user.turn
        }
    }
    return jsonify(ret_data)
