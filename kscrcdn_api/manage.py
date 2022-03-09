import sys, os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from kscrcdn_api.myapp import create_app
from kscrcdn_api.common import logger, db
from kscrcdn_api.config import settings

from flask_apidoc.commands import GenerateApiDoc
from flask_script import Manager
from flask_apidoc import ApiDoc


app = create_app(settings.DEBUG)
doc = ApiDoc(app)


logconfg = {
    'root': {
        'filename': {
            'INFO': os.path.join(BASE_DIR, settings.LOG_PATH),
            'ERROR': os.path.join(BASE_DIR, settings.ERROR_LOG_PATH)
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

manager = Manager(app)
manager.add_command('apidoc', GenerateApiDoc(output_path=os.path.join(BASE_DIR, 'doc/apidoc')))

@manager.command
def runserver():
    app.run(host=settings.HOST, port=settings.PORT, debug=settings.DEBUG)

if __name__ == '__main__':

    logger.install(logconfg)
    db.install(DATABASE)

    manager.run()