#coding:utf-8
import uuid

from flask import Blueprint, request
from sqlalchemy import text

from database.mysqlutil import MysqlUtil

from loguru import logger

from database.redisutil import RedisUtil
from utils import vuejson
from jsonschema import validate


import hashlib



from utils.catetree import generate_tree
from utils.exceptionutil import ExceptionUtil

#导入表名
from config.mysql.globalmysqltablename import rule_talbename,user_role_tablename,user_tablename,role_rule_tablename



user = Blueprint('user',__name__)



"""
    添加用户
"""
@user.route('/insertuser',methods=["POST"])
def insertuser():

    #1。验证参数
    add_user_data = request.get_json(silent=True)
    logger.debug(add_user_data)

    add_role_data_schema = {
        "type": "object",
        "properties": {
            "username": {
                "description": "用户名只能大小写字母和数字，不能使用特殊字符",
                "type": "string",
                "pattern": "^[a-zA-Z0-9]{1,16}$"
            },
            "password": {
                "description": "密码，需要验证两个是否相等",
                "type": "string",
                "pattern": "^[a-zA-Z0-9]{1,16}$",
            },
        },
        "required": [
            "username",
            "password",
            "role_id"
        ]
    }

    try:
        validate(instance=add_user_data, schema=add_role_data_schema)
    except Exception as e:
        logger.debug(e.message)
        return vuejson.json_params_error(message=e.message)


    username = add_user_data["username"]
    password = add_user_data["password"]
    role_id = add_user_data["role_id"]

    #2。判断数据库中是否有相同的用户名
    if publicselectduplicatename(username):
        return vuejson.json_result(code=400, message="用户名已经存在")



    # mysqlengine = MysqlUtil.init()

    # with mysqlengine.begin() as conn:
    #
    #     select_params_dict = {
    #         "username": username,
    #     }
    #
    #     username_equal_sql = "select username from admin where username = :username"
    #
    #     result = conn.execute(text(username_equal_sql),select_params_dict).first()
    #
    #     if result is not None:
    #         logger.debug("空结果 ")
    #         return vuejson.json_result(code=400,message="用户名已经存在")




    logger.debug("判断完用户名是否相等后，插入数据到用户表")

    mysqlengine = MysqlUtil.init()

    #3.将角色写入数据库
    with mysqlengine.begin() as conn:

        md5 = hashlib.md5()
        md5.update(password.encode('utf-8'))

        insert_params_dict = {
            "username": username,
            "password": md5.hexdigest()
        }

        add_role_data_sql = "insert into {user_tablename} (username,password) values (:username,:password)"\
                            .format(user_tablename=user_tablename)

        result = conn.execute(text(add_role_data_sql),insert_params_dict)

        logger.debug("看看结果是:"+str(result.lastrowid))



    # 4.将角色id,和用户id关联起来，插入到用户角色的中间表
    with mysqlengine.begin() as conn:

        insert_params_dict = {
            "user_id": result.lastrowid,
            "role_id": role_id
        }

        add_role_data_sql = "insert into {user_role_tablename} (user_id,role_id) values (:user_id,:role_id)"\
                            .format(user_role_tablename=user_role_tablename)

        result = conn.execute(text(add_role_data_sql),insert_params_dict)

    return vuejson.json_success(message="添加角色成功")


"""
    分页显示用户
"""
@user.route('/selectuser',methods=['POST'])
def selectuser():

    userdata = request.get_json(silent=True)
    logger.debug(userdata)

    schema = {
        "type": "object",
        "properties": {
            "pagesize": {
                "type": "integer",
                #匹配正整数
                # "pattern": "^[1-9]\d*$"
                "minimum": 1,
                # "exclusiveMaximum": 100
                "description": "需要传入每页显示多少数据"
            },
            "pagenum": {
                "type": "integer",
                "minimum": 1,
                "description": "需要传入页数"
            },
            "query": {
                "type": "string",
                # "pattern": "^[a-f]{40}$",
                # "miniLength": 2
                "description":"这是中文语言"
            }
        },
        "required": [
            "pagesize",
            "pagenum",
            "query",
        ]
    }

    try:
        validate(instance=userdata, schema=schema)
    except Exception as error:

        message = ExceptionUtil.json_errer_message(str(error))

        return vuejson.json_params_error(message=message)

    # try:
    #     validate(instance=userdata, schema=schema)
    # except Exception as e:
    #     logger.debug(e.message)
    #     return vuejson.json_params_error(message=e.message)

    # 获取分页信息
    page = userdata['pagenum']
    page_size = userdata['pagesize']

    # 先获取分页总数
    total_sql = "select count(*) from {user_tablename}".format(user_tablename=user_tablename)
    # 再获取对应页面的数据
    offset = (page - 1) * page_size

    mysqlengine = MysqlUtil.init()

    with mysqlengine.begin() as conn:
        result = conn.execute(text(total_sql)).fetchall()

    logger.debug("分頁总数是: " + str(result[0][0]))
    total =  result[0][0]

    #判断有没有收到分页参数
    sql = "select * from {user_tablename} order by id limit :page_size offset :offset".format(user_tablename=user_tablename)

    logger.debug(sql)

    with mysqlengine.begin() as conn:

        select_params_dict = {
            "page_size":page_size,
            "offset":offset
        }

        result = conn.execute(text(sql),select_params_dict).fetchall()


    logger.debug("获取的总数据是:")
    logger.debug(result)

    vuedata_user = []

    for data in result:
        mysql_user_data = {"id": data[0], "username": data[1]}

        vuedata_user.append(mysql_user_data)

    return vuejson.json_mysql_paginate(code=200,data=vuedata_user,message="获取用户数据成功",total=total)




"""
    根据id删除角色数据,并且将admin_role中间表数据删除
"""
@user.route('/deleteuser',methods=['POST'])
def deleteuser():

    userdata = request.get_json(silent=True)
    logger.debug(userdata)

    schema = {
        "type": "object",
        "properties": {
            "id": {
                "type": "integer",
                "minimum": 1,
            }
        },
        "required": [
            "id",
        ]
    }

    try:
        validate(instance=userdata, schema=schema)
    except Exception as e:
        logger.debug(e.message)
        return vuejson.json_params_error(message=e.message)

    if userdata["id"] == 1:
        return vuejson.json_success(message="管理员不能删除")

    mysqlengine = MysqlUtil.init()

    #1。先删除admin表数据
    sql = """
            delete from {user_tablename} where id = :id
        """.format(user_tablename=user_tablename)

    with mysqlengine.begin() as conn:

        delete_params_dict = {
            "id":userdata["id"],
        }

        result = conn.execute(text(sql),delete_params_dict)


    #2。再删除admin表数据
    sql = "delete from {user_role_tablename} where user_id = :id".format(user_role_tablename=user_role_tablename)

    with mysqlengine.begin() as conn:

        delete_params_dict = {
            "id":userdata["id"],
        }

        result = conn.execute(text(sql),delete_params_dict)

    logger.debug("获取的总数据是:")
    logger.debug(result)


    return vuejson.json_success(message="删除用户成功")



"""
    编辑用户时，需在将admin_role中间表，关联的一条角色数据返回给前端
"""
@user.route('/selectoneuserrole',methods=['POST'])
def selectoneuserrole():

    userdata = request.get_json(silent=True)
    logger.debug(userdata)

    schema = {
        "type": "object",
        "properties": {
            "user_id": {
                "type": "integer",
                "minimum": 1,
            }
        },
        "required": [
            "user_id",
        ]
    }

    try:
        validate(instance=userdata, schema=schema)
    except Exception as e:
        logger.debug(e.message)
        return vuejson.json_params_error(message=e.message)

    mysqlengine = MysqlUtil.init()

    #1。根据
    sql = "select role_id from {user_role_tablename} where user_id = :user_id".format(user_role_tablename=user_role_tablename)

    with mysqlengine.begin() as conn:

        select_params_dict = {
            "user_id":userdata["user_id"],
        }

        result = conn.execute(text(sql),select_params_dict)



    user_source = []

    for data in result:
        mysql_user_data = {"role_id": data[0]}

        user_source.append(mysql_user_data)

    return vuejson.json_success(data=user_source,message="获取角色数据成功")


"""
    根据id更新用户数据
"""
@user.route('/updateuser',methods=['POST'])
def updateuser():

    userdata = request.get_json(silent=True)
    logger.debug(userdata)



    schema = {
        "type": "object",
        "properties": {
            "id": {
                "type": "integer",
                "minimum": 1,
            },
            "username": {
                "description": "用户名只能大小写字母和数字，不能使用特殊字符",
                "type": "string",
                "pattern": "^[a-zA-Z0-9]{1,16}$"
            },
            "role_id": {
                "type": "integer",
                "minimum": 1,
            },
        },
        "required": [
            "id",
            "username",
            "role_id"
        ]
    }

    try:
        validate(instance=userdata, schema=schema)
    except Exception as e:
        logger.debug(e.message)
        return vuejson.json_params_error(message=e.message)


    id = userdata["id"]
    role_id = userdata["role_id"]
    username = userdata["username"]
    password = userdata["password"]


    #这里加多一个判断，如果是admin,id为1的超级管理员用户，不能修改admin用户名
    if id == 1:
        logger.debug("这里加多一个判断，如果是admin,id为1的超级管理员用户，不能修改admin用户名")
        username = 'admin'

    #如果密码为空,将密码参数去掉
    # mysql多字段更新，中间使用，逗号分隔
    if userdata["password"] == '':
        logger.debug("密码参数为空")

        sql = "update {user_tablename} set username = :username where id = :id".format(user_tablename=user_tablename)

        edit_params_dict = {
            "id": id,
            "username": username
        }

    else:

        md5 = hashlib.md5()
        md5.update(password.encode('utf-8'))

        edit_params_dict = {
            "id": id,
            "username": username,
            "password": md5.hexdigest()
        }

        sql = "update {user_tablename} set username = :username, password = :password  where id = :id".format(user_tablename=user_tablename)


    logger.debug(sql)

    #1.先查询有没有相同的用户名
    if publicselectduplicatename(username,id):
        return vuejson.json_result(code=400, message="用户名已经存在")

    #2。再更新对应的用户数据
    mysqlengine = MysqlUtil.init()

    with mysqlengine.begin() as conn:

        result = conn.execute(text(sql),edit_params_dict)

    #3.再把admin_role中间表的对应关系更新
    with mysqlengine.begin() as conn:

        edit_params_dict = {
            "user_id": id,
            "role_id": role_id
        }

        sql = "update {user_role_tablename} set role_id = :role_id where user_id = :user_id".format(user_role_tablename=user_role_tablename)

        logger.debug(sql)

        result = conn.execute(text(sql),edit_params_dict)

    return vuejson.json_success(message="更新角色成功")


"""
    抽取公共函数，查询是否有相同的用户名
"""
def publicselectduplicatename(username,userid=''):

    mysqlengine = MysqlUtil.init()

    with mysqlengine.begin() as conn:

        select_params_dict = {
            "id": userid,
            "username": username
        }

        if userid== '':
            #添加用户时，没有id
            username_equal_sql = "select username from {user_tablename} where username = :username".format(user_tablename=user_tablename)
        else:
            #更新用户时，带id参数
            username_equal_sql = "select username from {user_tablename} where username = :username and id != :id".format(user_tablename=user_tablename)

        result = conn.execute(text(username_equal_sql),select_params_dict).first()
        logger.debug("有重复的用户名????????????????")
        logger.debug(result)

        if result is not None:
            logger.debug("有重复的用户名")
            return True

    return False





#登录后台接口
@user.route('/login',methods=['POST'])
def login():

    userdata = request.get_json(silent=True)

    logger.debug(userdata)

    #验证参数
    schema = {
        "type": "object",
        "properties": {
            "username": {
                "description": "用户名只能小写字母和数字(不能大写)，不能使用特殊字符,长度是30",
                "type": "string",
                "pattern": "^[a-z0-9]{1,30}$",
            },
            "password": {
                "description": "密码使用md5,会转换成一串字符，所以暂时不用过滤",
                "type": "string",
                "pattern": "^[a-z0-9]{1,30}$",
            },
        },
        "required": [
            "username",
            "password"
        ]
    }

    try:
        validate(instance=userdata, schema=schema)
    except Exception as error:

        message = ExceptionUtil.json_errer_message(str(error))

        return vuejson.json_params_error(message=message)

    username = userdata["username"]
    password = userdata["password"]

    #1。从数据库中查询用户名和密码
    mysqlengine = MysqlUtil.init()

    md5 = hashlib.md5()
    md5.update(password.encode('utf-8'))

    with mysqlengine.begin() as conn:
        select_params_dict = {
            "username": username,
            "password": md5.hexdigest()
        }

        sql = """
                select * from {user_tablename} where username = :username and password = :password
            """.format(user_tablename=user_tablename)

        result = conn.execute(text(sql), select_params_dict).fetchall()

    #判断是否有查出用户信息
    if result:
        username = request.json.get('username')

        #生成一个随机uuid
        tokenid = uuid.uuid1()

        #把token放到redis缓存
        #新增功能 多用户登录时，存多个token
        redis = RedisUtil.init()
        #将用户名和token调转，可以存多个token
        # redis.hset("logintokenid", username, str(tokenid))


        # redis.hset("logintokenid", str(tokenid), username)
        from config.redis.rediskeyname import username_token_redis_keyname
        redis.sadd(username_token_redis_keyname + username, str(tokenid))

        #设置用户权限
        #menu_tree是导航菜单
        #user_rule_list是权限菜单
        menu_tree,user_rule_list = user_rule(username)

        #将权限菜单放到redis缓存
        redis.hset("menulist",username,str(user_rule_list))

        return vuejson.json_success(message="信息发送成功",
                                    data={"token": tokenid,
                                          "username": request.json.get('username'),
                                          "menu": menu_tree
                                          }
                                    )

    else:
        return vuejson.json_result(code=500,message="请输入正确的账号密码")




"""
    设置用户权限
"""
def user_rule(username):
    # 分析用户权限信息

    # 是否检查用户权限
    is_check_rule = True

    if username == 'admin':
        # 超级管理员，全部放行，不过还是需要获取全部菜单
        logger.debug("超级管理员")
        # 不验证权限
        is_check_rule = False

        sql = "select * from {rule_talbename}".format(rule_talbename=rule_talbename)

    else:
        logger.debug("普通用户")
        sql = """
                   select * from user_role join {role_rule_tablename} on {role_rule_tablename}.role_id={user_role_tablename}.role_id 
                   join {rule_talbename} on {rule_talbename}.id={role_rule_tablename}.rule_id 
                   where user_id=(select id from {user_tablename} where username='{username}')
                 """.format(user_role_tablename=user_role_tablename,
                            rule_talbename=rule_talbename,
                            user_tablename=user_tablename,
                            role_rule_tablename=role_rule_tablename,
                            username=username
                            )

    # logger.debug(sql)

    mysqlengine = MysqlUtil.init()

    with mysqlengine.begin() as conn:

        # select_params_dict = {
        #     "page_size": page_size,
        #     "offset": offset
        # }

        result = conn.execute(text(sql)).fetchall()

        mysql_rule_data = [dict(zip(result_data.keys(), result_data)) for result_data in result]

    logger.debug("获取到权限数据")
    # logger.debug(mysql_rule_data)

    # 用户权限列表
    user_rule_list = []
    # vue左侧导航菜单列表
    vue_left_menu = []

    for data in mysql_rule_data:
        # url = data["module_name"] + "/" + data["controller_name"] + "/" + data["action_name"]

        #在前面补一个/斜线,刚好补齐vue左侧菜单和redis缓存权限
        url = "/" + data["module_name"] + "/" + data["controller_name"] + "/" + data["action_name"]

        # 把所有字符中的大写字母转换成小写字母
        url = url.lower()

        user_rule_list.append(url)
        # logger.debug(url)

        # 需要考虑返回当前用户的导航菜单
        # is_show 等于1才会显示到vue左侧菜单
        if data["is_show"]:
            vue_left_menu.append(data)


    menu_tree = generate_tree(vue_left_menu, 0)

    # logger.debug("这。。。。。。。。。。。。。。。。。。")
    logger.debug(menu_tree)

    return menu_tree,user_rule_list



