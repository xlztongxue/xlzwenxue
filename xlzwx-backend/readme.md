### 部署

* 创建数据库

  ```mysql
  create database hmwx charset=utf8;
  ```

* 创建虚拟环境

  ```
  mkvirtualenv -p python3 hmwx
  pip install -r requirements.txt
  ```

* 迁移数据库-使用模型类生成表

  ```shell
  # 初始化
  python manage.py db init
  # 生成迁移脚本
  python manage.py db migrate
  # 升级(执行迁移脚本)
  python manage.py db upgrade
  ```

* 初始化数据

  ```shell
  # 初始化分类
  python manage_book.py init_category
  # 添加飞浪书籍数据
  python manage_book.py update_book -c feilang
  ```

* 运行代码

  ```shell
  # uwsgi conf/uwsgi_applet.ini
  gunicorn -w 4 -b 172.16.86.171:5000 wsgi_applet:app
  ```

* 测试

  ```
  # 搜索书籍
  /search/books
  # 获取书籍的章节列表
  /book/chapters/<int:book_id>
  # 获取章节内容
  /book/reader/<int:book_id>?chapterID=1
  ```

* 备注

  ```
  manage_book.py 主要用于修改数据库中的某些内容，具体的请看脚本文件
  运行格式: python manage_book.py 函数名称 
  ```

