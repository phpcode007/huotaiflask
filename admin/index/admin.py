#coding:utf-8
#user
import hashlib

from flask import Blueprint, render_template, redirect,request
from sqlalchemy import text

from database.mysqlutil import MysqlUtil
from utils.catetree import generate_tree

admin = Blueprint('admin',__name__)

from markupsafe import escape
from flask import session

from utils import vuejson

# from cacheout import Cache
from database.redisutil import RedisUtil

import uuid

from loguru import logger





# @admin.before_request
# def print_request_info():
#     print("请求地址：" + str(request.path))
#     print("请求方法：" + str(request.method))
#     print("---请求headers--start--")
#     print(str(request.headers).rstrip())
#     print("---请求headers--end----")
#     print("GET参数：" + str(request.args))
#     print("POST参数：" + str(request.form))





# from  . import user






@admin.route('/index/<name>')
def index(name):
    #当返回 HTML （ Flask 中的默认响应类型）时，为了防止注入攻击，所有用户提 供的值在输出渲染前必须被转义。

    # 要操作URL （如 ?key = value ）中提交的参数可以使用args属性:
    searchword = request.args.get('pid','')
    print('打印: ' + searchword)

    return f'Hello, {escape(name)}'

@admin.route('/test1')
def test1():
    token = request.headers.get('token')

    # usename = session[request.json.get('username')]
    # print(usename)
    print(session)
    print(request.headers)

    return vuejson.json_success(data={'ok':'123'})


# 用 Flask 处理文件上传很容易，只要确保不要忘记在您的 HTML 表单中设置 enctype="multipart/form-data" 属性就可以了。
# 否则浏览器将不会传送您的文件。
@admin.route('/upload')
def upload_file():
    if request.method == 'POST':
        f = request.files['the_file']
        f.save('/var/www/uploads/uploaded_file.txt')



