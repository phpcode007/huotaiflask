#coding:utf-8
from flask import Blueprint, render_template, redirect, request, session

from loguru import logger
from sqlalchemy import text

from database.mysqlutil import MysqlUtil
from utils import vuejson
from jsonschema import validate

from utils.exceptionutil import ExceptionUtil

role = Blueprint('role',__name__)

"""
    添加角色
"""
@role.route('/addrole',methods=["POST"])
def addrole():

    #1。验证参数
    add_role_data = request.get_json(silent=True)
    logger.debug(add_role_data)

    add_role_data_schema = {
        "type": "object",
        "properties": {
            "role_name": {
                "description": "角色名称只能是中文，数字和英文，不能包含特殊字符",
                "type": "string",
                # "pattern": "^[\u4e00-\u9fa5]+$",
                "pattern": "^[\u4E00-\u9FA5A-Za-z0-9]+$",
            }
        },
        "required": [
            "role_name",
        ]
    }

    try:
        validate(instance=add_role_data, schema=add_role_data_schema)
    except Exception as error:

        message = ExceptionUtil.json_errer_message(str(error))

        return vuejson.json_params_error(message=message)

    mysqlengine = MysqlUtil.init()

    #2。先判断数据库中没有相同的角色名
    with mysqlengine.begin() as conn:

        select_params_dict = {
            "role_name": add_role_data['role_name'],
        }

        username_equal_sql = "select role_name from role where role_name = :role_name"

        result = conn.execute(text(username_equal_sql),select_params_dict).first()

        logger.debug("##################################################")
        logger.debug(result)
        logger.debug("##################################################")


        if result is not None:
            logger.debug("空结果 ")
            return vuejson.json_result(code=400,message="角色名已经存在")

    #3.将角色写入数据库
    with mysqlengine.begin() as conn:

        insert_params_dict = {
            "role_name": add_role_data['role_name']
        }

        add_role_data_sql = "insert into role (role_name) values (:role_name)"

        result = conn.execute(text(add_role_data_sql),insert_params_dict)

    return vuejson.json_success(message="添加角色成功")


"""
    显示全部角色，所有数据传给添加用户页面表单
"""
@role.route('/allrole',methods=['POST'])
def allrole():

    catedata = request.get_json(silent=True)

    mysqlengine = MysqlUtil.init()

    #判断有没有收到分页参数
    sql = "select * from role"

    with mysqlengine.begin() as conn:

        result = conn.execute(text(sql)).fetchall()

    role_source = []

    mysql_role_data = [dict(zip(result_data.keys(), result_data)) for result_data in result]
    logger.debug(mysql_role_data)

    for data in result:
        mysql_cate_data = {"value": data["id"], "label": data["role_name"]}

        role_source.append(mysql_cate_data)

    return vuejson.json_success(data=role_source,message="获取角色数据成功")






"""
    分页显示角色
"""
@role.route('/listrole',methods=['GET','POST'])
def listrole():

    logger.debug("开始。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。")

    catedata = request.get_json(silent=True)
    logger.debug("**************************************")
    logger.debug(catedata)
    logger.debug("**************************************")


    schema = {
        "type": "object",
        "properties": {
            "pagesize": {
                "type": "integer",
                #匹配正整数
                # "pattern": "^[1-9]\d*$"
                "minimum": 1,
                # "exclusiveMaximum": 100
            },
            "pagenum": {
                "type": "integer",
                "minimum": 1,
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
        validate(instance=catedata, schema=schema)
    except Exception as e:
        logger.debug(e.message)
        return vuejson.json_params_error(message=e.message)

    # 获取分页信息
    page = catedata['pagenum']
    page_size = catedata['pagesize']

    # 先获取分页总数
    total_sql = "select count(*) from role"
    # 再获取对应页面的数据
    offset = (page - 1) * page_size

    mysqlengine = MysqlUtil.init()

    with mysqlengine.begin() as conn:
        result = conn.execute(text(total_sql)).fetchall()

    logger.debug("分頁总数是: " + str(result[0][0]))
    total =  result[0][0]

    #判断有没有收到分页参数
    sql = "select * from role  order by id limit :page_size offset :offset"

    logger.debug(sql)

    with mysqlengine.begin() as conn:

        select_params_dict = {
            "page_size":page_size,
            "offset":offset
        }

        result = conn.execute(text(sql),select_params_dict).fetchall()


    logger.debug("获取的总数据是:")
    logger.debug(result)

    role_source = []

    for data in result:
        mysql_cate_data = {"id": data[0], "role_name": data[1]}

        role_source.append(mysql_cate_data)

    return vuejson.json_mysql_paginate(code=200,data=role_source,message="获取角色数据成功",total=total)







"""
    根据id删除角色数据
"""
@role.route('/deleterole',methods=['POST'])
def deleterole():

    roledata = request.get_json(silent=True)
    logger.debug(roledata)

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
        validate(instance=roledata, schema=schema)
    except Exception as e:
        logger.debug(e.message)
        return vuejson.json_params_error(message=e.message)

    mysqlengine = MysqlUtil.init()

    #判断有没有收到分页参数
    sql = "delete from role where id = :id"

    with mysqlengine.begin() as conn:

        delete_params_dict = {
            "id":roledata["id"],
        }

        result = conn.execute(text(sql),delete_params_dict)


    logger.debug("获取的总数据是:")
    logger.debug(result)


    return vuejson.json_success(message="删除角色成功")





"""
    根据id更新角色数据
"""
@role.route('/editrole',methods=['POST'])
def editrole():

    roledata = request.get_json(silent=True)
    logger.debug(roledata)

    schema = {
        "type": "object",
        "properties": {
            "id": {
                "type": "integer",
                # "pattern": "^[\-|0-9][0-9]{1,}$",
                "minimum": 1,
            },
            "role_name": {
                "description": "角色名称只能是中文，数字和英文,不能包含特殊字符",
                "type": "string",
                "pattern": "^[\u4E00-\u9FA5A-Za-z0-9]+$",
            }
        },
        "required": [
            "id",
            "role_name"
        ]
    }

    try:
        validate(instance=roledata, schema=schema)
    except Exception as e:
        logger.debug(e.message)
        return vuejson.json_params_error(message=e.message)

    mysqlengine = MysqlUtil.init()

    #判断有没有收到分页参数
    sql = "update role set role_name = :role_name where id = :id"

    with mysqlengine.begin() as conn:

        edit_params_dict = {
            "id":roledata["id"],
            "role_name": roledata["role_name"]
        }

        result = conn.execute(text(sql),edit_params_dict)


    # logger.debug("获取的总数据是:")
    # logger.debug(result)


    return vuejson.json_success(message="更新角色成功")


"""
    添加角色对应权限
"""
@role.route('/insertroleandrule',methods=["POST"])
def insertroleandrule():

    #1。验证参数
    insert_role_and_rule_data = request.get_json(silent=True)
    logger.debug(insert_role_and_rule_data)
    logger.debug(insert_role_and_rule_data["allruleids"])
    # logger.debug(insert_role_and_rule_data["allruleids"][0])
    # logger.debug(insert_role_and_rule_data["allruleids"][1])

    role_id = insert_role_and_rule_data["role_id"]

    # add_role_data_schema = {
    #     "type": "object",
    #     "properties": {
    #         "role_name": {
    #             "description": "角色名称只能是中文，不能包含数字和英文和特殊字符",
    #             "type": "string",
    #             "pattern": "^[\u4e00-\u9fa5]+$",
    #         }
    #     },
    #     "required": [
    #         "role_name",
    #     ]
    # }
    #
    # try:
    #     validate(instance=add_role_data, schema=add_role_data_schema)
    # except Exception as e:
    #     logger.debug(e.message)
    #     return vuejson.json_params_error(message=e.message)

    mysqlengine = MysqlUtil.init()

    #2。先判断数据库中没有相同的角色名
    with mysqlengine.begin() as conn:

        #事务1，先删除 role_rule中间表中 对应role_id数据
        conn.execute(text("delete from role_rule where role_id = :role_id"),{"role_id":role_id})

        #事务2，再插入多条权限数据
        # values = [
        #     {"id":"1", "role_id":"2", "rule_id":"3"},
        #     {"id":"2", "role_id":"2", "rule_id":"3"},
        #     {"id": "3", "role_id": "2", "rule_id": "3"}
        #     # ('1', '2', '3')
        # ]

        ruleid_values = []

        if len(insert_role_and_rule_data["allruleids"]) <= 1:
            logger.debug("少于1")



        for i in insert_role_and_rule_data["allruleids"]:
            logger.debug("??????????")
            logger.debug(i)
            ruleid_values.append({"role_id":role_id, "rule_id":i})

        conn.execute(text("INSERT INTO role_rule (role_id, rule_id) VALUES (:role_id,:rule_id)"), ruleid_values)

        conn.commit()

    return vuejson.json_success(message="添加角色成功")