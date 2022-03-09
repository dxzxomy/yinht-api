#!/usr/bin/env python3
# -*- coding:utf-8 -*-
from kscrcdn_api.config import settings
from kscrcdn_api.common import logger, db
from kscrcdn_api.myapp import create_app

logconfg = {
    'root': {
        'filename': {
            'INFO': settings.LOG_PATH,
            'ERROR': settings.ERROR_LOG_PATH
        }
    }
}

DATABASE = {
    'yinht': {
        'engine': settings.DB_ENGINE,
        'user': settings.DB_USER,
        'host': settings.DB_HOST,
        'system': settings.DB_USER,
        'passwd': settings.DB_PASSWORD,
        'db': settings.DB_NAME,
        'charset': settings.DB_CHARSET,
        'conn': settings.DB_CONN,
        'port': settings.DB_PORT
    },
}


if settings.DEBUG:
    logger.install('stdout')
else:
    # logger.install(logconfg, when="midnight", backupCount=60)
    logger.install(logconfg)

db.install(DATABASE)
app = create_app()

if __name__ == '__main__':
   app.run(host=settings.HOST, port=settings.PORT, debug=settings.DEBUG)

