# windows环境下需要使用本机ip地址作为host
HOST = '0.0.0.0'
PORT = 18080

# mysql settings
DB_NAME = 'yinht'
DB_ENGINE = 'pymysql'
DB_HOST = 'mysql-server'
DB_PORT = 3306
DB_USER = 'omy'
DB_PASSWORD = 'Sanchuang123#'
DB_CONN = 300
DB_CHARSET = 'utf8'

DEBUG = False
LOG_PATH = 'log/kscrcdn_api.log'
ERROR_LOG_PATH = 'log/kscrcdn_api.error.log'

# 数据目录
DATADIR = 'data'

# 文件服务器
FILE_HOST = 'http://120.92.215.53:9005'
FILE_USER = 'mingguangzhen'
FILE_PASS = 'mingguangzhen'
PXE_MD5 = '07b05d5c0a391958cb124b6f0305b327'
INIT_MD5 = 'c121efb646c05935cf136ad168be5828'



try:
    from kscrcdn_api.config.local_settings import *
except:
    pass