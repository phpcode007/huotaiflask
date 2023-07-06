#coding:utf-8
#user
from flask import Blueprint
rbac = Blueprint('rbac',__name__)

from flask import request

@rbac.route('/index')
def index():
    return '权限首页'

@rbac.route('/add',methods=['GET','POST'])
def add():
    # 如果从视图返回一个dict ，那么它会被转换为一个JSON响应。
    #如果 dict 还不能满足需求，还需要创建其他类型的 JSON 格式响应，可以使用 jsonify() 函数。
    return {
        'errno':0,
        'message': '用户名',
        'data' : {'token':'dafdaf'}
    }


@rbac.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        return '开始登录'
    else:
        return '展示登录页面，和thinkphp差不多的做法'