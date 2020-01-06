from flask import Blueprint, current_app
from flask import jsonify
from flask_restful import Api, Resource
from flask import g
import random

from lib.decorators import api_login_required, login_required
from models import db
from models import User
from models import Book
from models import ReadRate
from models import BookChapters

from models import BookShelf

bp = Blueprint('mybooks', __name__)


@bp.route('/')
@login_required
def mybooks_list():
    """
    我的书架-列表
    :return:
    """
    mybooks = BookShelf.query.filter_by(user_id=g.user_id).order_by(BookShelf.created.desc()).all()
    data = []
    if not mybooks:
        books = Book.query.all()
        bs_books = random.sample(books, 5)
        for book in bs_books:
            bs = BookShelf(user_id=g.user_id,
                           book_id=book.book_id,
                           book_name=book.book_name,
                           cover=book.cover)
            db.session.add(bs)
            data.append({
                'id': book.book_id,
                'imgURL': 'http://{}/{}'.format(current_app.config['QINIU_SETTINGS']['host'], book.cover),
                'title': book.book_name
            })
        db.session.commit()
        return jsonify(data)
    else:
        for bs in mybooks:
            data.append({
                'id': bs.book_id,
                'imgURL': 'http://{}/{}'.format(current_app.config['QINIU_SETTINGS']['host'], bs.cover),
                'title': bs.book_name
            })
        return jsonify(data)


api = Api(bp)


class MyBooksLast(Resource):
    """
    最后阅读
    """
    method_decorators = {
        'get': [api_login_required]
    }
    def get(self):
        user = User.query.get(g.user_id)
        read_rate = None
        if not user.last_read:
            book = Book.query.first()
            user.last_read = book.book_id
            chapter = BookChapters.query.filter_by(book_id=book.book_id)\
                        .order_by(BookChapters.chapter_id.asc()).first()
            user.last_read_chapter_id = chapter.chapter_id
            read_rate = ReadRate(
                            user_id=user.id,
                            book_id=book.book_id,
                            chapter_id=chapter.chapter_id,
                            chapter_name=chapter.chapter_name
                        )
            db.session.add(read_rate)
            db.session.add(user)
            db.session.commit()
        else:
            book = Book.query.get(user.last_read)

        if not read_rate:
            read_rate = ReadRate.query.filter_by(user_id=user.id,
                                                 book_id=book.book_id,
                                                 chapter_id=user.last_read_chapter_id).first()
        data = {
            'id': book.book_id,
            'title': book.book_name,
            'chapter': read_rate.chapter_name,
            'progress': read_rate.rate,
            'imgURL': 'http://{}/{}'.format(current_app.config['QINIU_SETTINGS']['host'],book.cover)
        }
        return data


class MyBooksResource(Resource):
    """
    书架-添加, 删除
    """
    method_decorators = [api_login_required]

    def post(self, book_id):
        book = Book.query.get(book_id)
        if not book:
            return {'msg': '不存在该书籍'}, 404
        bs = BookShelf.query.filter_by(user_id=g.user_id, book_id=book_id).first()
        if not bs:
            db.session.add(BookShelf(user_id=g.user_id,
                                     book_id=book.book_id,
                                     book_name=book.book_name,
                                     cover=book.cover))
            db.session.commit()
            return jsonify({'msg': '添加成功'})
        return {'msg': '已存在书架中'}, 403


    def delete(self, book_id):
        bs = BookShelf.query.filter_by(book_id=book_id, user_id=g.user_id).first()
        if not bs:
            return {'msg': '您的书架不存在该书籍'}, 403
        db.session.delete(bs)
        db.session.commit()
        return {'msg': '删除成功'}


api.add_resource(MyBooksLast, '/last')
api.add_resource(MyBooksResource, '/<int:book_id>')



