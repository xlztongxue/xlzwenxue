"""
Doc: 加载飞浪的书籍

Created on 2019/6/5
@author: wzq
"""
import os
import codecs
import datetime
import copy

from script.base_spider import BaseBookSpider


class FeilangBookSpider(BaseBookSpider):
    """飞浪"""
    CHANNEL_NAME = 'feilang'
    start_book_id = 1501
    books = {}  # 初始化的时候就遍历文件夹，把所有书都存在books
    prefix = 'script'

    def __init__(self):
        self.chapter_num_dict = {}  # 保存书籍章节数量
        self.init_books()


    def get_file_names(self, path):
        """
        获取script/path 目录下所有文件的文件名
        :param path:
        :return:
        """
        files =  os.listdir('%s/%s' %(self.prefix, path))
        file_list = [f for f in files]
        return file_list 

    def get_id_title(self, line):
        """
        获取章节id和章节名称
        :param line:
        :return:
        """
        text = line[line.find(u'§')+1:]
        text = text.strip().replace('\r\n','')
        end_num = 0
        for i, s in enumerate(text):
            if s not in '1234567890':
                end_num = i
                break
        _id = int(text[:end_num].strip()) + 1
        title = text[end_num:].strip()
        return _id, title

    def get_chapters(self, f):
        """
        获取所有章节
        :param f:
        :return:
        """
        chapters = []
        data = {}
        for line in f:
            if '§' in line:
                if data:
                    chapters.append(copy.copy(data))
                data['chapter_id'], data['chapter_name'] = self.get_id_title(line)
                data['content'] = ''
            else:
                if data:
                    data['content'] += line
        return chapters


    def init_books(self):
        """
        初始化所有书籍，把数据全部准备好。
        :return:
        """
        book_list = self.get_file_names(self.CHANNEL_NAME)
        for book_name in book_list:
            book_data = dict(book_name=book_name)
            path = '%s/%s' %(self.CHANNEL_NAME, book_name)
            book_files = self.get_file_names(path)
            for bf in book_files:
                if '简介' in bf:
                    with codecs.open('%s/%s/%s' %(self.prefix, path, bf), 'r', 'gbk') as f:
                        book_data['intro'] = f.read().encode('utf-8')
                elif '.txt' not in bf:
                    file_path = '%s/%s/%s' %(self.prefix, path, bf)
                    book_data['cover'] = file_path
                else:
                    filename = '%s/%s/%s' %(self.prefix, path, bf)
                    with codecs.open(filename, 'r', 'gbk') as f:
                        book_data['chapters'] = self.get_chapters(f)

            self.books[self.start_book_id] = book_data
            self.start_book_id += 1


    def get_book_list(self, local_cate_dict):
        """获取书籍列表"""
        if not self.books:
            return []

        # 获取本地已有分类
        book_list = []
        for _book_id in self.books:
            book_id = int(_book_id)
            book = self.books[_book_id]
            print(local_cate_dict)
            cate_id = local_cate_dict.get('都市生活')
            if not cate_id:
                print('NO cate_id: ')
                continue
            book_list.append(dict(book_id=book_id,
                                  book_name=book['book_name'],
                                  cate_id=cate_id,
                                  cate_name='都市生活',
                                  channel_type= 1,
                                  author_name='',
                                  chapter_num=0,
                                  is_publish=2,
                                  status=1,
                                  create_time=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                  cover=book['cover'],
                                  intro=book.get('intro', ''),
                                  word_count=0,
                                  source=self.CHANNEL_NAME,
                                  update_time=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),))
        return book_list


    def get_volume_chapter_list(self, channel_book_id, max_cid, local_book_id):
        """获取卷和章节列表"""
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        if not self.books.get(channel_book_id):
            return [], []

        data = self.books[channel_book_id]['chapters']
        volume_list = []
        chapter_list = []
        for chap in data:
            chapter_list.append({
                'book_id': local_book_id,
                'volume_id': 0,
                'volume_name': '',
                'chapter_id': chap['chapter_id'],
                'chapter_name': chap['chapter_name'],
                'word_count': cal_word_count(chap['content']),
                'create_time': now,
                'update_time': now,
                'content': chap['content']
            })
        self.chapter_num_dict[channel_book_id] = int(data[-1]['chapter_id']) if data else 0
        return volume_list, chapter_list


    def need_update_chap_num(self):
        return True

    def get_chap_num(self, channel_book_id):
        return self.chapter_num_dict.get(channel_book_id, 0)


def cal_word_count(content):
    """计算章节字数 只计算中英文"""
    num = 0
    for i in content:
        if is_chinese(i) or is_letter(i):
            num += 1
    return num


def is_chinese(u_char):
    """判断一个unicode是否是汉字"""
    return u'\u4e00' <= u_char <= u'\u9fa5'


def is_num(u_char):
    """判断一个unicode是否是数字"""
    return u'\u0030' <= u_char <= u'\u0039'


def is_letter(u_char):
    """判断一个unicode是否是英文字母"""
    return (u'\u0041' <= u_char <= u'\u005a') or (u'\u0061' <= u_char <= u'\u007a')

