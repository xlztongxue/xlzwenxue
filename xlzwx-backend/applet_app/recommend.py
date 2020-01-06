from flask import Blueprint, current_app
from flask.json import jsonify
from flask_restful import Api

from models import *

bp = Blueprint('recommend', __name__)

api = Api(bp)

@bp.route('/hots/<int:cate_id>')
def hot_books(cate_id):
    """
    推荐-同类热门推荐
    推荐返回 4 条
    :param cate_id:
    :return:
    """
    big_cate = BookBigCategory.query.get(cate_id)
    books = []
    if big_cate:
        second_ids = [i.cate_id for i in big_cate.second_cates]
        o_books = Book.query.filter(Book.cate_id.in_(second_ids)).limit(4)
        for item in o_books:
            books.append({
            'id': item.book_id,
            'title': item.book_name,
            'introduction': item.intro,
            'author': item.author_name,
            'state': item.status,
            'categoryID': item.cate_id,
            'categoryName': item.cate_name,
            'imgURL': 'http://{}/{}'.format(current_app.config['QINIU_SETTINGS']['host'], item.cover)
        })
    else:
        o_books = Book.query.limit(4)
        for item in o_books:
            books.append({
            'id': item.book_id,
            'title': item.book_name,
            'introduction': item.intro,
            'author': item.author_name,
            'state': item.status,
            'categoryID': item.cate_id,
            'categoryName': item.cate_name,
            'imgURL': 'http://{}/{}'.format(current_app.config['QINIU_SETTINGS']['host'], item.cover)
        })
    return jsonify(books)
