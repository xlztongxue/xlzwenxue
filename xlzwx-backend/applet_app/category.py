from flask import Blueprint, request, jsonify, current_app
from flask_restful import Api
from sqlalchemy import and_

from models import *
from lib.decorators import login_required

bp = Blueprint('category', __name__)

api = Api(bp)

#
@bp.route('/filters')
def book_list():
    """
    分类-书本列表-筛选
    :return:
    """
    page = request.args.get('page', 1, int)
    pagesize = request.args.get('pagesize', 10, int)
    categoryID = request.args.get('categoryID', 0, int) # 一级分类id(大分类)
    # 字数类型ID
    # 0 所有
    # 1 50万字以下
    # 2 50~100万字
    # 3 100万字以上
    words = request.args.get('words', -1, int)
    order = request.args.get('order', 1, int) # 排序 1 按最热 2 按收藏
    if not categoryID:
        return jsonify({'msg':'缺少一级分类id'}), 400
    cate = BookBigCategory.query.get(categoryID)
    second_ids = set([i.cate_id for i in cate.second_cates])
    query = Book.query.filter(Book.cate_id.in_(second_ids))
    if words == 1:
        query = query.filter(Book.word_count < 500000)
    elif words == 2:
        query = query.filter(Book.word_count.between(500000, 1000000))
    elif words == 3:
        query = query.filter(Book.word_count > 1000000)

    if order == 1:
        query = query.order_by(Book.heat.desc())
    elif order == 2:
        query = query.order_by(Book.collect_count.desc())
    else:
        return jsonify({'msg': '错误的order选项'}), 400
    # paginate = News.query.filter(*query_condition).order_by(News.create_time.desc()).paginate(page, 10, False)
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
    print(dir(paginate))

    return jsonify(data)



@bp.route('/')
def categorys_list():
    """
    返回大类列表
    :return:
    """
    gender = request.args.get('gender', 1, int)
    big_cates = BookBigCategory.query.filter_by(channel=gender).all()
    data = []
    for big_cate in big_cates:
        big_tmp = {
            'id': big_cate.cate_id,
            'title': big_cate.cate_name,
            'imgURL': 'http://{}/{}'.format(current_app.config['QINIU_SETTINGS']['host'], big_cate.icon),
            'subCategorys': []
        }

        # 获取二级分类
        for cate in big_cate.second_cates:
            tmp = {
                'id': cate.cate_id,
                'title': cate.cate_name
            }
            big_tmp['subCategorys'].append(tmp)
        data.append(big_tmp)

    return jsonify(data)