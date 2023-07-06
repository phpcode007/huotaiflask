from config.globalconfig import DEBUG,PROD_DEBUG
from config.globalconfig import MYSQL_HOST,MYSQL_PORT,MYSQL_USER,MYSQL_PASSWORD,MYSQL_DATABASENAME
from config.globalconfig import REDIS_HOST,REDIS_PORT,REDIS_PASSWORD

# 默认配置
class BaseConfig:
    # 基础配置
    DEBUG = DEBUG


    #mysql测试数据库配置
    MYSQL_USER = MYSQL_USER
    MYSQL_PASSWORD = MYSQL_PASSWORD
    MYSQL_HOST = MYSQL_HOST
    MYSQL_PORT = MYSQL_PORT
    MYSQL_DATABASENAME = MYSQL_DATABASENAME

    #redis配置
    REDIS_HOST = REDIS_HOST
    REDIS_PORT = REDIS_PORT
    REDIS_PASSWORD = REDIS_PASSWORD

# 开发环境
class DevConfig(BaseConfig):
    # 基础配置
    DEBUG = DEBUG
    # 数据库配置

    #宿舍
    # REDIS_PASSWORD = 'vueflasktest'



# 测试环境
class TestingConfig(DevConfig):
    # 基础配置
    DEBUG = DEBUG
    # 数据库配置

    #不能使用pass,这样不能继承
    # pass

# 生产环境
class ProdConfig(BaseConfig):
    # 基础配置
    DEBUG = PROD_DEBUG
    # 数据库配置


# 环境映射关系
config_choice = {
    "default": BaseConfig,
    "dev": DevConfig,
    "test": TestingConfig,
    "prod": ProdConfig
}