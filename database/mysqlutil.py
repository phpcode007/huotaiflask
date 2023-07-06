#!/usr/bin/python3.10
# -*- coding: utf-8 -*-

from loguru import logger
from sqlalchemy import create_engine

from config.globalconfig import CONFIG_MODE

class MysqlSingleton(object):

    engine = None

    @classmethod
    def init(cls):

        logger.debug("*************开始初始化数据库连接******************")

        if cls.engine:
            logger.debug("已经存在一个mysql初始化实例")
            return cls.engine

        #导入配置文件类，读取数据库配置文件
        from config.flask.flaskconfig import config_choice
        mysqlconfig = config_choice.get(CONFIG_MODE)

        mysql_host = mysqlconfig.MYSQL_HOST
        mysql_port = mysqlconfig.MYSQL_PORT
        mysql_user = mysqlconfig.MYSQL_USER
        mysql_password = mysqlconfig.MYSQL_PASSWORD
        mysql_databasename = mysqlconfig.MYSQL_DATABASENAME

        #例子
        #"mysql+pymysql://root:8289792@192.168.62.130:3306/xjq?charset=utf8"
        #这里不能换行，换行的话，mysql配置文件连不上
        sqlconnect = """mysql+pymysql://{mysql_user}:{mysql_password}@{mysql_host}:{mysql_port}/{mysql_databasename}?charset=utf8"""\
                        .format(mysql_user=mysql_user,
                       mysql_password=mysql_password,
                       mysql_host=mysql_host,
                       mysql_port=mysql_port,
                       mysql_databasename=mysql_databasename
                       )

        logger.debug("会不断连接@@@@@@@@@@消耗mysql 资源吗？？？？？？！！！")


        cls.engine = create_engine(sqlconnect,
                                   echo=True,
                                   echo_pool=True,
                                   future=True,
                                   pool_size=20,
                                   max_overflow=10,
                                   pool_timeout=30,
                                   pool_pre_ping=True
                                   )
        #要返回这个类变量，这样才能判断到是不是为空
        return cls.engine

#由于gunicorn开了4线程，所以看日志有4次初始化的过程，是正常的
MysqlUtil = MysqlSingleton()
