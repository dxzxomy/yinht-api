# -*- coding:utf-8 -*-
try:
    from kscrcdn_api.myapp import create_app
    from kscrcdn_api.common import logger, db
    from kscrcdn_api.config import settings
except:
    import sys, os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from kscrcdn_api.myapp import create_app
    from kscrcdn_api.common import logger, db
    from kscrcdn_api.config import settings


app = create_app(settings.DEBUG)
# from flask_cors import CORS
# cors = CORS(app)

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

if __name__ == '__main__':
    if settings.DEBUG:
        logger.install('stdout')
    else:
        logger.install(logconfg, when="midnight", backupCount=60)
    if db.dbpool is None:
        db.install(DATABASE)
    app.run(host=settings.HOST, port=settings.PORT, debug=settings.DEBUG)
