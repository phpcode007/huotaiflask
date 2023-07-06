from flask import  jsonify


#返回值的规范（就算值为空，我们也必须返回以下字段）
# {
#   "code": 200,   #状态码
#   "message": "",  #信息提示
#   "data": {},  #返回的数据，比如文章列表等等
# }
#
#
# 状态码的规范
#
# 200：成功
# 401：没有授权
# 400：参数错误
# 405:方法错误
# 500：服务器错误

#普通用法xjson.json_result(code=200, message='', data={})

class StatusCode(object):
    ok = 200
    paramserror = 400
    unauth = 401
    methoderror = 405
    servererror = 500

def json_result(code, message, data={}):
    return jsonify({"code": code, "message":str(message), "data":data or {}})


def json_success(message='', data=None):
    return json_result(code=StatusCode.ok, message=message, data=data)

# 报错：Uncaught (in promise) TypeError: root2.forEach is not a function
# 错误原因：传入的数据不符合格式
# 遇见场合：el-tabel中传入了一个对象给data
# 所以这里直接返回列表
#checkboxdata 是vue树形组件多选框是否选定数组
def json_success_vue_array(message='', data=None, checkboxdata = None, vxetabledata = None):
    return jsonify({"code": StatusCode.ok,
                    "message":message,
                    "data":data or [],
                    "checkboxdata":checkboxdata or [],
                    "vxetabledata": vxetabledata or []
                    })

def json_params_error(message='', data=None):
    """
     请求参数错误
    """
    return json_result(code=StatusCode.paramserror, message=message, data=data)

def json_unauth_error(message='', data=None):
    """
    没有权限访问
    """
    return json_result(code=StatusCode.unauth, message=message, data=data)

def json_method_error(message='', data=None):
    """
    请求方法错误
    """
    return json_result(code=StatusCode.methoderror, message=message, data=data)

def json_server_error(message='', data=None):
    """
    服务器内部错误
    """
    return json_result(code=StatusCode.servererror, message=message, data=data)

"""
这个是单独出来的，不和上面的函数复用，只为获取到表总数据
"""
def json_mysql_paginate(code, message, data, total):
    """
    分页数据,单独返回一个数据库表数据的总数
    """
    return jsonify({"code": code, "message":message, "data":data or {}, "total":total})

