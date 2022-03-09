import celery
import logging
import traceback
from kscrcdn_api.common import db
from kscrcdn_api.common import dbalias as dba
from kscrcdn_api.common.tools import with_json

log = logging.getLogger()


class MyCeleryTask(celery.Task):
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        data = dict(
            task_id=task_id, result=with_json(repr(exc)), task_name=self.name,
            args=with_json(args), kwargs=with_json(kwargs), status=0,
        )
        self.record_result(data)

    def on_success(self, retval, task_id, args, kwargs):
        data = dict(
            task_id=task_id, result=with_json(retval), task_name=self.name,
            args=with_json(args), kwargs=with_json(kwargs), status=1,
        )
        self.record_result(data)

    def on_retry(self, exc, task_id, args, kwargs, einfo):
        log.debug(f'{exc=}, {task_id=}, {args=}, {kwargs=}, {einfo=}')

    @staticmethod
    def record_result(data):
        try:
            with db.get_connection(dba.dbn) as conn:
                conn.insert(dba.celery_ret, data)
        except:
            log.error(traceback.format_exc())


