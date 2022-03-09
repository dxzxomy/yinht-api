import logging

log = logging.getLogger()


class BasePlugin:
    def __init__(self, func=None):
        self._func = func

    def __call__(self, last_ret=None):
        self.last_ret = last_ret
        return self.doitself()

    def doitself(self):
        log.debug('doitself')
        return "What?"
