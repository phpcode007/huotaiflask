#!/usr/bin/python3.10
# -*- coding: utf-8 -*-

import redis
from loguru import logger
from config.globalconfig import CONFIG_MODE


class RedisSingleton:

    redis_engine = None

    @classmethod
    def init(cls):

        if cls.redis_engine:
            logger.debug("已经存在一个redis初始化实例")
            return cls.redis_engine

        #导入配置文件类，读取数据库配置文件
        from config.flask.flaskconfig import config_choice
        redisconfig = config_choice.get(CONFIG_MODE)

        redis_host = redisconfig.REDIS_HOST
        redis_port = redisconfig.REDIS_PORT
        redis_password = redisconfig.REDIS_PASSWORD

        #decode_responses=True
        #Python3与redis交互驱动上存在问题，如果使用python2则不会出现这样的问题。同样在python3打印数据中b'开头的代表的是bytes类型数据.
        cls.redis_engine = redis.Redis(host=redis_host, port=redis_port, password=redis_password, db=0,decode_responses=True)

        logger.debug("会不断连接消耗redis 资源吗？？？？？？！！！")

        #要返回这个类变量，这样才能判断到是不是为空
        return cls.redis_engine

#单例模式，先初始化
#由于gunicorn开了4线程，所以看日志有4次初始化的过程，是正常的
RedisUtil = RedisSingleton()