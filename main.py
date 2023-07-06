#!/usr/bin/python3.10
# -*- coding: utf-8 -*-

#pip install redis
#pip install pymysql
#pip install sqlalchemy
#日志系统
#pip install loguru
#表单验证
#pip3 install wtforms


#在linux系统，没有安装上面的依赖会报错
#Error: While importing 'app', an ImportError was raised.

# from form.validatorall import LoginForm
from loguru import logger
# import json

from flask import Flask, request

from database.redisutil import RedisUtil
from public.publicread import PUBLIC_LOGIN_URL

from utils import vuejson

#导入表名


app = Flask(__name__)


# def setup_loguru(app,log_level='WARNING'):
#     logger.add(
#         'logs/{time:%Y-%m-%d}.log',
#         level='DEBUG',
#         format='{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}',
#         backtrace=False,
#         rotation='00:00',
#         retention='20 days',
#         encoding='utf-8'
#     )
#
#     app.logger.addHandler(InterceptHandler())
#     logging.basicConfig(handlers=[InterceptHandler()], level=log_level)


#这个是解决json返回中文乱码问题
app.config['JSON_AS_ASCII'] = False

# Set the secret key to some random bytes. Keep this really secret!
# app.secret_key = b'dsaf@dsafdA123'

#flask从json文件读取配置文件
# app.config.from_file("config/flaskconfig.json", load=json.load)

# import toml
# app.config.from_file("config.toml", load=toml.load)
# print(app.config['SECRET_KEY'])
# CORS(app, supports_credentials=True)  # 关键是这一句设置跨域
# app.config['SESSION_COOKIE_SAMESITE'] = "None"  # 设置samesite 为None



#用对象管理配置文件
#开发时需要一套配置，测试需要一套，生产需要一套，
#通过使用对象引入的方式来多种环境下的配置编写。

from config.flask.flaskconfig import config_choice
import os

config_env = os.getenv('FLASK_CONFIG') or 'dev'
app.config.from_object(config_choice.get(config_env))



result = ''

from admin.index.admin import admin
from admin.rbac.rbac import rbac
from index.index.index import index
from admin.rbac.user import user
from admin.index.category import category
from admin.rbac.role import role
from admin.rbac.rule import rule

app.register_blueprint(rbac,url_prefix='/admin/rbac')
app.register_blueprint(index,url_prefix='/index/index')
app.register_blueprint(admin,url_prefix='/admin/admin')

app.register_blueprint(user,url_prefix='/admin/user')

#加入分类
app.register_blueprint(category,url_prefix='/admin/category')

#加入角色管理
app.register_blueprint(role,url_prefix='/admin/role')

#加入权限模块
app.register_blueprint(rule,url_prefix='/admin/rule')


# logger.add("xjq.log")



#全局拦截session和权限处理

# 该方法先判断请求是否是普通请求（图片等不做处理，这里是示例，直接写死了只对ico文件不处理，实际有问题）。
# 如果是普通请求，判断是否是login 请求。
# 如果不是login 请求，再判断session中是否已经有 username（也就是是否已经登录），如果没有则跳转到login页面。

@app.before_request
def before_action():
    print(request.path)
    print('全局拦截模块')
    if request.path.find('.ico')==-1:
        if not request.path== PUBLIC_LOGIN_URL:

            #获取用户传过来的tokenid
            username = request.headers['username']
            user_token_id = request.headers['token']

            #从redis获取token
            redis = RedisUtil.init()

            # redis_token_id = redis.hget("logintokenid",username)
            #更换为多用户登录，查询token
            #由于hash没有针对单个字段，设置过期时间
            #换为集合存储
            from config.redis.rediskeyname import username_token_redis_keyname
            redis_token_id = redis.sismember(username_token_redis_keyname + username, user_token_id)


            logger.debug(username)
            logger.debug(".................................................")
            logger.debug(redis_token_id)

            # if user_token_id != redis_token_id:
            if redis_token_id == False:
                #返回600状态码，让客户端接到自动退出登录
                return vuejson.json_result(code=600,data={},message="您还没有登录,请先退出后台再登录")

            #分析用户权限信息



            #从redis获取权限菜单
            redis_menulist = redis.hget("menulist", username)
            logger.debug("全局权限菜单验证")
            logger.debug(redis_menulist)
            logger.debug(request.path)

            # 和用户请示的url进行权限匹配
            # if request.path in redis_menulist:
            #     logger.debug("权限验证通过")
            # else:
            #     logger.debug("权限验证失败")
            #     return vuejson.json_result(code=500, data={}, message="权限验证失败")

