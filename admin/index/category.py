#coding:utf-8
import json

from loguru import logger
from flask import Blueprint, render_template, redirect, request, session
from sqlalchemy import text

# from form.validatorall import LoginForm
from utils import vuejson
from utils.catetree import generate_tree,has_parent_data

from database.mysqlutil import MysqlUtil

category = Blueprint('category',__name__)


#获取全部分类数据
@category.route('/allcate',methods=['GET','POST'])
def allcate():

    catedata = request.get_json(silent=True)
    logger.debug(catedata)

    from jsonschema import validate
    schema = {
        "type": "object",
        "properties": {
            "pagesize": {
                "type": "number",
            },
            "pagenum": {
                "type": "number"
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
    total_sql = "select count(*) from category"
    # 再获取对应页面的数据
    # if page == 1:
    #     offset = page * page_size
    # else:
    offset = (page - 1) * page_size


    mysqlengine = MysqlUtil.init()

    with mysqlengine.begin() as conn:
        result = conn.execute(text(total_sql)).fetchall()

    logger.debug("分頁总数是: " + str(result[0][0]))
    total =  result[0][0]

    #判断有没有收到分页参数
    if page and page_size:
        # 例子：展示第3页，每页展示6条
        # sql = "insert into category (cname,parent_id,isrec) VALUES (:cname,:parent_id,:isrec)"
        # sql = "select * from category limit " + str(page_size) + " offset " + str(offset)
        sql = "select * from category limit :page_size offset :offset"


    logger.debug(sql)

    with mysqlengine.begin() as conn:

        select_params_dict = {
            "page_size":page_size,
            "offset":offset
        }

        result = conn.execute(text(sql),select_params_dict).fetchall()


    logger.debug("获取的总数据是:")
    logger.debug(result)

    permission_source = []

    for data in result:
        mysql_cate_data = {"id": data[0], "label": data[1], "parent_id": data[2], "isrec": data[3], "value": data[0],"path": "/admin/category/listcate"}

        permission_source.append(mysql_cate_data)

    return vuejson.json_mysql_paginate(code=200,data=permission_source,message="获取菜单成功",total=total)





@category.route('/listcate',methods=['GET','POST'])
def listcate():


    mysqlengine = MysqlUtil.init()

    with mysqlengine.begin() as conn:
        sql = "select * from category"

        result = conn.execute(text(sql)).fetchall()


    # permission_source = [{"id": 1, "label": '顶级菜单', "path": "/admin/category/listcate", "parent_id": 0,"value": 0}]
    permission_source = []

    for data in result:
        print(data[0],data[1],data[2])
        # mysql_cate_data = {"id": data[0], "label": data[1], "value": data[2], "isrec": data[3],"path":"/api1"}
        mysql_cate_data = {"id": data[0], "label": data[1], "parent_id": data[2],"isrec": data[3],"value":data[0],"path": "/admin/category/listcate"}




        permission_source.append(mysql_cate_data)

    user1 = {"id": 101, "label": "用户管理", "parent_id": 0, "isrec": 1, "value": 90,"path": "/admin/user/listuser"}
    user2 = {"id": 102, "label": "用户管理", "parent_id": 101, "isrec": 1, "value": 91, "path": "/admin/user/listuser"}
    user3 = {"id": 103, "label": "角色管理", "parent_id": 101, "isrec": 1, "value": 92, "path": "/admin/role/addrole"}

    user4 = {"id": 104, "label": "权限管理", "parent_id": 101, "isrec": 1, "value": 93, "path": "/admin/rule/addrule"}


    permission_source.append(user1)
    permission_source.append(user2)
    permission_source.append(user3)
    permission_source.append(user4)

    #insert into category values (null,'分类列表',0,1);


    #value是给前端vue树形组件使用的,而且值不能相同
    #id和parent_id是给python后端格式化树状结构使用的

    # permission_source = [
    #     {"id": 1, "label": '数码', "path": "/admin/category/listcate", "parent_id": 0, "value": 1},
    #     {"id": 2, "label": '手机', "path": "/admin/category/listcate",  "parent_id": 1, "value": 2},
    #     {"id": 3, "label": '笔记本', "path": "/admin/category/listcate",  "parent_id": 1, "value": 3},
    #     {"id": 4, "label": '水果', "path": "/admin/category/listcate",  "parent_id": 0, "value": 4},
    #     {"id": 5, "label": '龙眼', "path": "/admin/category/listcate",  "parent_id": 4, "value": 5},
    #     {"id": 6, "label": '西瓜', "path": "/admin/category/listcate",  "parent_id": 4, "value": 6},
    #     {"id": 7, "label": '生活用品', "path": "/admin/category/listcate",  "parent_id": 0, "value": 7},
    #     {"id": 8, "label": '母婴', "path": "/admin/category/listcate",  "parent_id": 0, "value": 8},
    #     {"id": 9, "label": '顶级菜单', "path": "/admin/category/listcate", "parent_id": 0, "value": 0},
    # ]
    # permission_source.append({"id": 2, "label": '手机', "path": "/admin/category/listcate",  "parent_id": 1, "value": 2})

    # logger.debug(permission_source)

    permission_tree = generate_tree(permission_source, 0)

    # logger.debug(permission_tree)
    # permission_tree.append(user)

    return vuejson.json_success(data=permission_tree,message="获取菜单成功")

@category.route('/addcate',methods=['POST'])
def addcate():
    # axios不同于普通的Ajax，这表现在，当发起Ajax时，post的数据其实是一个FormData，而axios则是一个PayLoad，
    # 所以，在接收数据的方法上略有不同。（Ajax的接收方法是：request.form.get(‘aa’)
    # 或者直接resquest.form[‘aa’]）
    catedata = request.get_json(silent=True)

    logger.debug(catedata)

    #参数验证
    form = LoginForm()
    if form.validate_on_submit():
        errors = form.errors
        logger.debug(errors)

    mysqlengine = MysqlUtil.init()

    with mysqlengine.begin() as conn:
        sql = "insert into category (cname,parent_id,isrec) VALUES (:cname,:parent_id,:isrec)"

        result = conn.execute(text(sql),{"cname":catedata['cname'], "parent_id":catedata['parent_id'], "isrec":catedata['isrec']})

    return vuejson.json_success(message="添加分类成功")

#删除分类
@category.route('/deletecate',methods=['POST'])
def deletecate():
    logger.debug("开始删除分类数据")
    catedata = request.get_json(silent=True)
    logger.debug(catedata)

    #1。从数据库查询出所有的分类数据
    mysqlengine = MysqlUtil.init()

    with mysqlengine.begin() as conn:
        sql = "select * from category"

        result = conn.execute(text(sql)).fetchall()

    #2。检查是不是还有父ID,如果还有父ID不允许删除，要先删除所有子分类才可以删除父分类
    permission_source = []

    for data in result:
        mysql_cate_data = {"id": data[0], "parent_id": data[2]}

        permission_source.append(mysql_cate_data)

    is_delete_cate = has_parent_data(permission_source, catedata["id"], catedata["parent_id"])

    if is_delete_cate:

        with mysqlengine.begin() as conn:
            sql = "delete from category where id = :id"

            result = conn.execute(text(sql), {"id": catedata['id']})

        return vuejson.json_success(message="删除分类成功")

    return vuejson.json_result(code=500,data={},message="这个分类下面还有子分类，请先删除子分类后，再来删除这个分类")