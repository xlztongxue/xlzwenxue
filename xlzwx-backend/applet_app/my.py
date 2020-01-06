from flask import Blueprint, g, current_app, jsonify
from flask_restful import Api, Resource, inputs
from flask_restful.reqparse import RequestParser

from models import *
from lib.decorators import api_login_required

bp = Blueprint('my', __name__)

api = Api(bp)


class HistoryResource(Resource):
    """
    我的浏览记录
    """
    method_decorators = {
        'get': [api_login_required],
        'delete': [api_login_required]
    }

    def get(self):
        """
        获取我的浏览记录
        :return:
        """
        rp = RequestParser()
        rp.add_argument('page', type=inputs.positive, default=1, location='args')
        rp.add_argument('pagesize', type=inputs.positive, default=10, location='args')
        req = rp.parse_args()

        user = User.query.get(g.user_id)
        paginate = BrowseHistory.query.filter_by(user_id=g.user_id).paginate(req.page, req.pagesize, False)
        items = []
        for item in paginate.items:
            items.append({
                'id': item.book.book_id,
                'title': item.book.book_name,
                'author': item.book.author_name,
                'state': item.book.status,
                'imgURL': 'http://{}/{}'.format(current_app.config['QINIU_SETTINGS']['host'], item.book.cover),
                'lastTime': item.updated.strftime('%Y-%m-%d %H:%M:%S')
            })
        data = {
            'counts': paginate.total,
            'pagesize': req.pagesize,
            'pages': paginate.pages,
            'page': paginate.page,
            'items': items
        }
        return jsonify(data)


    def delete(self):
        """
        清空浏览记录
        :return:
        """
        historys = BrowseHistory.query.filter_by(user_id=g.user_id).all()
        for h in historys:
            db.session.delete(h)
        db.session.commit()
        return {'msg': 'ok'}

api.add_resource(HistoryResource, '/historys')