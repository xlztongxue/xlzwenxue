from flask import Blueprint, request, jsonify, current_app
from flask_restful import Api
from sqlalchemy import not_

from models import *

bp = Blueprint('search', __name__)

api = Api(bp)


@bp.route('/books')
def book_list():
    """
    搜索-书本列表-模糊
    :return:
    """
    page = request.args.get('page', 1, int)
    pagesize = request.args.get('get', 10, int)
    keyword = request.args.get('keyword')
    query = Book.query
    if keyword:
        query = query.filter(Book.book_name.contains(keyword))
    paginate = query.paginate(page, pagesize, False)
    items = []
    for item in paginate.items:
        items.append({
            'id': item.book_id,
            'title': item.book_name,
            'introduction': item.intro,
            'author': item.author_name,
            'state': item.status,
            'categoryID': item.cate_id,
            'categoryName': item.cate_name,
            'imgURL': 'http://{}/{}'.format(current_app.config['QINIU_SETTINGS']['host'], item.cover)
        })

    data = {
        'counts': paginate.total,
        'pagesize': pagesize,
        'pages': paginate.pages,
        'page': paginate.page,
        'items': items
    }
    return jsonify(data)


@bp.route('/tags')
def tag_list():
    """
    搜索-热门搜索词
    :return:
    """
    keyword = request.args.get('keyword')
    if not keyword:
        return jsonify([])
    keywords = SearchKeyWord.query.filter(SearchKeyWord.keyword.contains(keyword)).limit(10)
    data = [{
        'title': word.keyword,
        'isHot': word.is_hot
    } for word in keywords]
    return jsonify(data)


@bp.route('/recommendeds')
def recommended():
    """
    搜索-精准&高匹配&推荐
    :return:
    """
    keyword = request.args.get('keyword')
    # 插入关键字表
    skw = SearchKeyWord.query.filter_by(keyword=keyword).first()
    if not skw:
        skw = SearchKeyWord(keyword=keyword,
                            count=0)
    skw.count += 1
    if skw.count >= 10:
        skw.is_hot = True
    db.session.add(skw)
    db.session.commit()

    book_ids = []
    # 一条准确查询
    o_accurate = Book.query.filter_by(book_name=keyword).first()
    accurate = {}
    if o_accurate:
        accurate = {
            'id': o_accurate.book_id,
            'title': o_accurate.book_name,
            'introduction': o_accurate.intro,
            'author': o_accurate.author_name,
            'state': o_accurate.status,
            'categoryID': o_accurate.cate_id,
            'categoryName': o_accurate.cate_name,
            'imgURL': 'http://{}/{}'.format(current_app.config['QINIU_SETTINGS']['host'],o_accurate.cover),
        }
        book_ids.append(o_accurate.book_id)
    # 两条高匹配
    o_match = Book.query.filter(Book.book_name.contains(keyword),
                                not_(Book.book_id.in_(book_ids)))
    o_match = o_match.limit(2)
    match = []
    for book in o_match:
        match.append({
            'id': book.book_id,
            'title': book.book_name,
            'introduction': book.intro,
            'author': book.author_name,
            'state': book.status,
            'categoryID': book.cate_id,
            'categoryName': book.cate_name,
            'imgURL': 'http://{}/{}'.format(current_app.config['QINIU_SETTINGS']['host'],book.cover),
        })
        book_ids.append(book.book_id)

    # 4条推荐记录
    o_recommends = Book.query.filter(not_(Book.book_id.in_(book_ids))).limit(4)
    recommends = []
    for book in o_recommends:
        recommends.append({
            'id': book.book_id,
            'title': book.book_name,
            'introduction': book.intro,
            'author': book.author_name,
            'state': book.status,
            'categoryID': book.cate_id,
            'categoryName': book.cate_name,
            'imgURL': 'http://{}/{}'.format(current_app.config['QINIU_SETTINGS']['host'], book.cover),
        })
    data = {
        'accurate': accurate,
        'match': match,
        'recommends': recommends,
    }

    return jsonify(data)
