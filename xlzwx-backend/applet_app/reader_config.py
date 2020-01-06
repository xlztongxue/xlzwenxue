from flask import Blueprint, request, jsonify, g
from flask_restful import Api, Resource
from lib.decorators import login_required

from models import User, db

bp = Blueprint('reader_config', __name__)

api = Api(bp)

@bp.route('/preference', methods=['POST'])
@login_required
def preference():
    """
    设置个人偏好
    :return:
    """
    gender = int(request.json.get('gender'))
    if gender not in (0,1):
        return jsonify({'msg': '错误的gender'}), 403
    user = User.query.get(g.user_id)
    user.preference = gender
    db.session.add(user)
    db.session.commit()
    return jsonify({'msg': '设置成功'})


@bp.route('/reader', methods=['POST'])
@login_required
def reader():
    """
    设置阅读器的配置
    :return:
    """
    brightness = request.json.get('brightness')
    fontSize = request.json.get('fontSize')
    background = request.json.get('background')
    turn = request.json.get('turn')

    user = User.query.get(g.user_id)
    if brightness:
        user.brightness = int(brightness)

    if fontSize:
        user.fontSize = int(fontSize)

    if background:
        user.background = background

    if turn:
        user.turn = turn

    db.session.add(user)
    db.session.commit()
    return jsonify({'msg': '设置成功'})

