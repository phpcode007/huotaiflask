#coding:utf-8
#user
from flask import Blueprint, render_template, redirect
index = Blueprint('index',__name__)

@index.route('/index')
#由于这个路由和系统提供的路由冲突，需要在前面加一个下划线进行区分
def _index():
    return '测试首页'