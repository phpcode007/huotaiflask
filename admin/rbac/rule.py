#coding:utf-8
from flask import Blueprint, render_template, redirect, request, session

from loguru import logger
from sqlalchemy import text

from database.mysqlutil import MysqlUtil
from utils import vuejson
from jsonschema import validate

from utils.catetree import generate_tree, has_parent_data

rule = Blueprint('rule',__name__)

"""
    添加权限
"""
@rule.route('/addrule',methods=["POST"])
def addrule():

    #1。验证参数
    add_rule_data = request.get_json(silent=True)
    logger.debug(add_rule_data)

    add_rule_data_schema = {
        "type": "object",
        "properties": {
            "rule_name": {
                "description": "权限名称只能是中文，不能包含数字和英文和特殊字符",
                "type": "string",
                "pattern": "^[\u4e00-\u9fa5]+$",
            },
            "module_name": {
                "description": "模块名称只能是英文字母，不能包含数字和特殊字符",
                "type": "string",
                "pattern": "[a-zA-Z]",
            },
            "controller_name": {
                "description": "控制器名称只能是英文字母，不能包含数字和特殊字符",
                "type": "string",
                "pattern": "[a-zA-Z]",
            },
            "action_name": {
                "description": "方法名称只能是英文字母，不能包含数字和特殊字符",
                "type": "string",
                "pattern": "[a-zA-Z]",
            },
            "parent_id": {
                "description": "父类ID，匹配正整数,只能从1开始",
                "type": "integer",
                "minimum": 0,
            },
            "is_show": {
                "description": "是否展示,匹配正整数,只能从1开始",
                "type": "integer",
                "minimum": 0,
            },
        },
        "required": [
            "rule_name",
            "module_name",
            "controller_name",
            "action_name",
            "parent_id",
            "is_show"
        ]
    }

    try:
        validate(instance=add_rule_data, schema=add_rule_data_schema)
    except Exception as e:
        logger.debug(e.message)
        return vuejson.json_params_error(message=e.message)

    mysqlengine = MysqlUtil.init()

    #2。先判断数据库中没有相同的权限名称
    with mysqlengine.begin() as conn:

        select_params_dict = {
            "rule_name": add_rule_data['rule_name'],
        }

        username_equal_sql = "select rule_name from rule where rule_name = :rule_name"

        result = conn.execute(text(username_equal_sql),select_params_dict).first()

        if result is not None:
            logger.debug("空结果 ")
            return vuejson.json_result(code=400,message="权限名已经存在")

    #3.将权限写入数据库
    with mysqlengine.begin() as conn:

        insert_params_dict = {
            "rule_name": add_rule_data['rule_name'],
            "module_name": add_rule_data['module_name'],
            "controller_name": add_rule_data['controller_name'],
            "action_name": add_rule_data['action_name'],
            "parent_id": add_rule_data['parent_id'],
            "is_show": add_rule_data['is_show']
        }

        add_rule_data_sql = "insert into rule (rule_name,module_name,controller_name,action_name,parent_id,is_show) " \
                            "values (:rule_name,:module_name,:controller_name,:action_name,:parent_id,:is_show)"

        result = conn.execute(text(add_rule_data_sql),insert_params_dict)

    return vuejson.json_success(message="添加权限成功")


# """
#     显示全部权限，所有数据传给添加权限页面表单
# """
# @rule.route('/allrule',methods=['GET','POST'])
# def allrule():
#
#     ruledata = request.get_json(silent=True)
#     logger.debug(ruledata)
#
#     mysqlengine = MysqlUtil.init()
#
#     #判断有没有收到分页参数
#     sql = "select * from rule"
#
#     logger.debug(sql)
#
#     with mysqlengine.begin() as conn:
#
#         result = conn.execute(text(sql)).fetchall()
#
#     rule_source = []
#
#     for data in result:
#         mysql_rule_data = {"value": data[0], "label": data[1]}
#
#         rule_source.append(mysql_rule_data)
#
#     return vuejson.json_success(data=rule_source,message="获取权限数据成功")



"""
    分页显示权限
"""
@rule.route('/listrule',methods=['GET','POST'])
def listrule():

    ruledata = request.get_json(silent=True)
    logger.debug(ruledata)

    if str(ruledata) != '{}':
        role_id = ruledata["role_id"]
    else:
        role_id = 100;


    # schema = {
    #     "type": "object",
    #     "properties": {
    #         "pagesize": {
    #             "type": "integer",
    #             #匹配正整数
    #             # "pattern": "^[1-9]\d*$"
    #             "minimum": 1,
    #             # "exclusiveMaximum": 100
    #         },
    #         "pagenum": {
    #             "type": "integer",
    #             "minimum": 1,
    #         },
    #         "query": {
    #             "type": "string",
    #             # "pattern": "^[a-f]{40}$",
    #             # "miniLength": 2
    #             "description":"这是中文语言"
    #         }
    #     },
    #     "required": [
    #         "pagesize",
    #         "pagenum",
    #         "query",
    #     ]
    # }
    #
    # try:
    #     validate(instance=ruledata, schema=schema)
    # except Exception as e:
    #     logger.debug(e.message)
    #     return vuejson.json_params_error(message=e.message)

    # 获取分页信息
    # page = ruledata['pagenum']
    # page_size = ruledata['pagesize']

    # 先获取分页总数
    # total_sql = "select count(*) from role"
    # 再获取对应页面的数据
    # offset = (page - 1) * page_size

    mysqlengine = MysqlUtil.init()

    # with mysqlengine.begin() as conn:
    #     result = conn.execute(text(total_sql)).fetchall()
    # 
    # logger.debug("分頁总数是: " + str(result[0][0]))
    # total =  result[0][0]
    # 
    # #判断有没有收到分页参数
    # sql = "select * from role  order by id limit :page_size offset :offset"
    # 
    # logger.debug(sql)

    with mysqlengine.begin() as conn:
        sql = "select * from rule"

        result = conn.execute(text(sql)).fetchall()

        vxe_table_mysql_rule_data = [dict(zip(result1.keys(), result1)) for result1 in result]

    logger.debug("获取到所有权限数据")

    # logger.debug(mysql_rule_data)
    for data in vxe_table_mysql_rule_data:
        #由于tree数据需要两个属性,value和label
        #所以返回的数据添加两个属性value和label
        data["label"] = data["rule_name"]
        data["value"] = data["id"]



    logger.debug("权限数据")
    logger.debug(vxe_table_mysql_rule_data)
    #
    permission_tree = generate_tree(vxe_table_mysql_rule_data, 0)
    # permission_tree = vue_table_mysql_rule_data


    #第2步，需要将这个角色对应的已有权限从数据库取出来，给前端多选框展示


    with mysqlengine.begin() as conn:
        select_params_dict = {
            "role_id": role_id

        }

        sql = "select rule_id from role_rule where role_id = :role_id"

        result = conn.execute(text(sql),select_params_dict).fetchall()

        logger.debug(result)



        mysql_rule_data = [dict(zip(result1.keys(), result1)) for result1 in result]

        logger.debug(mysql_rule_data)

        #组装vue树形多选框默认选中数组
        vue_tree_checkbox_select_data = []

        for i in mysql_rule_data:
            logger.debug(i["rule_id"])
            vue_tree_checkbox_select_data.append(i["rule_id"])

        logger.debug(vue_tree_checkbox_select_data)

    """
        data 返回权限树
        checkboxdata 返回多选框选中
        vxetabledata 返回vxe表格数据
    """
    return vuejson.json_success_vue_array(data=permission_tree,
                                          checkboxdata=vue_tree_checkbox_select_data,
                                          vxetabledata=vxe_table_mysql_rule_data,
                                          message="获取权限成功"
                                          )










"""
    根据id删除权限数据
"""
@rule.route('/deleterule',methods=['POST'])
#删除权限
# @rule.route('/deletecate',methods=['POST'])
def deleterule():
    logger.debug("开始删除权限数据")
    ruledata = request.get_json(silent=True)
    logger.debug(ruledata)

    #1。从数据库查询出所有的权限数据
    mysqlengine = MysqlUtil.init()

    with mysqlengine.begin() as conn:
        sql = "select * from rule"

        result = conn.execute(text(sql)).fetchall()

    #2。检查是不是还有父ID,如果还有父ID不允许删除，要先删除所有子权限才可以删除父权限
    rule_source = []

    for data in result:
        mysql_rule_data = {"id": data[0], "parent_id": data[5]}

        rule_source.append(mysql_rule_data)

    is_delete_cate = has_parent_data(rule_source, ruledata["id"], ruledata["parent_id"])

    if is_delete_cate:

        with mysqlengine.begin() as conn:
            sql = "delete from rule where id = :id"

            result = conn.execute(text(sql), {"id": ruledata['id']})

        return vuejson.json_success(message="删除权限成功")

    return vuejson.json_result(code=500,data={},message="这个权限下面还有子权限，请先删除子权限后，再来删除这个权限")





"""
    根据id更新权限数据
"""
@rule.route('/editrule',methods=['POST'])
def editrule():

    ruledata = request.get_json(silent=True)
    logger.debug(ruledata)

    schema = {
        "type": "object",
        "properties": {
            "id": {
                "type": "integer",
                # "pattern": "^[\-|0-9][0-9]{1,}$",
                "minimum": 1,
            },
            "rule_name": {
                "description": "权限名称只能是中文，不能包含数字和英文和特殊字符",
                "type": "string",
                "pattern": "^[\u4e00-\u9fa5]+$",
            }
        },
        "required": [
            "id",
            "rule_name"
        ]
    }

    try:
        validate(instance=ruledata, schema=schema)
    except Exception as e:
        # logger.debug(e.message)
        return vuejson.json_params_error(message=e.message)

    mysqlengine = MysqlUtil.init()

    #判断有没有收到分页参数
    sql = """
        update rule set rule_name = :rule_name, 
                        module_name=:module_name, 
                        controller_name = :controller_name, 
                        action_name = :action_name,
                        parent_id = :parent_id,
                        is_show = :is_show
                        where id = :id
        """

    with mysqlengine.begin() as conn:

        edit_params_dict = {
            "rule_name": ruledata["rule_name"],
            "module_name": ruledata["module_name"],
            "controller_name": ruledata["controller_name"],
            "action_name": ruledata["action_name"],
            "parent_id": ruledata["parent_id"],
            "is_show": ruledata["is_show"],
            "id": ruledata["id"]
        }

        result = conn.execute(text(sql),edit_params_dict)


    return vuejson.json_success(message="更新权限成功")


