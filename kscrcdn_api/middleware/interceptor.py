import traceback
import logging
from functools import wraps

log = logging.getLogger()


class RequestWrapHandler:
    """请求拦截器
    """
    def __init__(self, class_plugins=None):
        self._func = None
        self.obj_plugins = []
        if class_plugins and (not isinstance(class_plugins, (list, tuple))):
            class_plugins = [class_plugins, ]
        elif not class_plugins:
            class_plugins = []
        self.class_plugins = class_plugins

    def __call__(self, func):
        wraps(func)(self)
        self._func = self.__wrapped__
        self.make_func()
        return self.call_func

    def make_func(self):
        self.obj_plugins = [plugin(self._func) for plugin in self.class_plugins]


class PostRequestWrapHandler(RequestWrapHandler):
    """请求处理后拦截器
    """
    def __init__(self, class_plugins=None):
        super(PostRequestWrapHandler, self).__init__(class_plugins)
        self.func_ret = None

    def call_func(self, *args, **kwargs):
        try:
            self.func_ret = self._func(*args, **kwargs)
            midret = self.func_ret
            # 用户token过期拦截
            log.debug(f'{midret=}')
            if isinstance(midret, dict) and midret.get('code') == 50014:
                return midret
            for obj_plugin in self.obj_plugins:
                midret = obj_plugin(midret)
            return midret
        except Exception as e:
            err = str(e)
            log.error(traceback.format_exc())
        return {'code': 20500, 'msg': f'Server Error: {err}'}


class PreRequestWrapHandler(RequestWrapHandler):
    """请求处理前拦截器
    """
    def __init__(self, class_plugins=None):
        super(PreRequestWrapHandler, self).__init__(class_plugins)

    def call_func(self, *args, **kwargs):
        for obj_plugin in self.obj_plugins:
            result = obj_plugin()
            if result:
                return result
        return self._func(*args, **kwargs)
