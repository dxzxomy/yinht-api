import redis
import time
import logging
from kscrcdn_api.config import settings

log = logging.getLogger()


class MyRedis:
    def __init__(self, host, port, password=None, db=1):
        self.__redis = redis.StrictRedis(
            host=host, port=port, db=db,
            password=password, decode_responses=True
        )

    def __getattr__(self, item):
        err = ''
        startm = time.perf_counter()
        try:
            return getattr(self.__redis, item)
        except Exception as e:
            err = str(e)
        finally:
            endtm = time.perf_counter()
            log.info(f'class=redis|func={item}|time={int((endtm-startm)*1000000)}|{err=}')


def cache(db_num=1):
    ins = MyRedis(settings.REDIS_HOST, settings.REDIS_PORT, settings.REDIS_PASSWORD, db=db_num)
    return ins
