from flask import Blueprint, g, request, current_app
from flask.json import jsonify
from flask_restful import Api, Resource

from models import *

bp = Blueprint('book', __name__)

api = Api(bp)


@bp.route('/<int:book_id>')
def detail(book_id):
    """
    获取书籍详情
    :param book_id:
    :return:
    """
    book = Book.query.get(book_id)
    if not book:
        return jsonify({'msg': '书籍不存在'}), 404

    # 添加浏览记录
    if g.user_id:
        bs = BrowseHistory.query.filter_by(user_id=g.user_id,
                                           book_id=book_id).first()
        if not bs:
            bs = BrowseHistory(user_id=g.user_id,
                               book_id=book_id)
        bs.updated = datetime.now()
        db.session.add(bs)
        db.session.commit()

    chapter = BookChapters.query.filter_by(book_id=book_id) \
        .order_by(BookChapters.chapter_id.desc()).first()
    # 返回数据
    data = {
        'id': book.book_id,
        'title': book.book_name,
        'introduction': book.intro,
        'author': book.author_name,
        'state': book.status,
        'categoryID': book.cate_id,
        'categoryName': book.cate_name,
        'imgURL': 'http://{}/{}'.format(current_app.config['QINIU_SETTINGS']['host'],book.cover),
        'words': book.word_count,
        'lastChapter': chapter.chapter_name if chapter else 'None',
    }
    return jsonify(data)


@bp.route('/reader/<int:book_id>')
def reader_book(book_id):
    """
    获取阅读进度
    :param book_id:
    :return:
    """
    book = Book.query.get(book_id)
    chapterID = request.args.get('chapterID', -1, int)
    if not book:
        return jsonify({'msg': '书籍不存在'}), 404
    if chapterID < 1:
        return jsonify({'msg': 'chapterID 不能小于1'}), 403

    chapter = BookChapters.query.get(chapterID)
    if not chapter:
        return jsonify({'msg': '章节不存在'}), 404
    content = BookChapterContent.query.filter_by(book_id=book_id,
                                              chapter_id=chapterID).first()

    # 获取用户进度
    progress = None
    if g.user_id:
        progress = ReadRate.query.filter_by(book_id=book_id,
                                         chapter_id=chapterID,
                                         user_id=g.user_id).first()
    # 返回数据
    data = {
        "id": book_id,
        "title": book.book_name,
        "chapterID": chapterID,
        "chapter": chapter.chapter_name,
        "progress": progress.rate if progress else 0,
        "article": content.content if content else ''
    }

    return jsonify(data)


@bp.route('/chapters/<int:book_id>')
def chapter_list(book_id):
    """
    获取章节列表
    :param book_id:
    :return:
    """
    page = request.args.get('page', 1, int)
    pagesize = request.args.get('pagesize', 10, int)
    order = request.args.get('order', 0, int) # 排序 0 正序 1 倒序

    book = Book.query.get(book_id)
    if not book:
        return jsonify({'msg': '书籍不存在'}), 404
    query = BookChapters.query.filter_by(book_id=book_id)
    if order == 1:
        query = query.order_by(BookChapters.chapter_id.desc())
    else:
        query = query.order_by(BookChapters.chapter_id.asc())

    # 分页
    paginate = query.paginate(page, pagesize, False)

    items = []
    for item in paginate.items:
        items.append({
            'id': item.chapter_id,
            'title': item.chapter_name
        })
    data = {
        'counts': paginate.total,
        'pagesize': pagesize,
        'pages': paginate.pages,
        'page': page,
        'items': items
    }
    return jsonify(data)