import re
import logging
from ..base import BasePlugin
from flask import request
from kscrcdn_api.common.ndb import cache
from kscrcdn_api.common import db
from kscrcdn_api.common import dbalias as dba
from kscrcdn_api.common.tools import with_json
from kscrcdn_api.common.tools import get_user_privs

log = logging.getLogger()


# 用户操作日志记录
class UserTraceHandlerPlugin(BasePlugin):

    def __init__(self, func):
        self.cache9 = cache(9)
        super(UserTraceHandlerPlugin, self).__init__(func)

    def get_token_by_oway(self):
        cookies = request.cookies.to_dict()
        rtree_token = cookies.get('rtree_token') or request.args.get('access_token')
        if not rtree_token:
            if self.last_ret and self.last_ret.get('data') and isinstance(self.last_ret['data'], dict):
                rtree_token = self.last_ret['data'].get('token', '')
        return rtree_token

    def doitself(self):
        rtree_token = self.get_token_by_oway()
        user_info = self.cache9.hgetall(rtree_token)
        if user_info and 'id' in user_info:
            user_id = user_info.get('id')
            path = request.path
            method = request.method
            args = request.args.to_dict()
            body = request.json
            response = self.last_ret
            with db.get_connection(dba.dbn) as conn:
                data = dict(
                    user_id=user_id, path=path, method=method,
                    args=with_json(args), body=with_json(body),
                    response=with_json(response, '"Not json api"')
                )
                conn.insert(dba.trace_record, data)
        log.debug('aberrant=%s|last_ret=%s', self._func.__dict__, self.last_ret)
        return self.last_ret


# 用户身份鉴权
class UserAuthentication(BasePlugin):

    def __init__(self, func):
        self.cache9 = cache(9)
        super(UserAuthentication, self).__init__(func)

    @staticmethod
    def find_privs(user_id, path, method):
        view_privs, api_privs = get_user_privs(user_id)
        for item in api_privs:
            log.debug(f'{item=}|{method=}')
            priv_path = item['path']
            priv_method = item['method']
            if re.search(f'{priv_path}', path) and re.search(f'{priv_method}', method):
                return True

    def doitself(self):
        """50008: Illegal token; 50012: Other clients logged in; 50014: Token expired;"""
        cookies = request.cookies.to_dict()
        rtree_token = cookies.get('rtree_token') or ''
        user_info = self.cache9.hgetall(rtree_token)
        path = request.path
        method = request.method
        if user_info:
            user_id = user_info['id']
            if self.find_privs(user_id, path, method):
                return
            return {'code': 20403, 'msg': '用户权限不足, 请联系管理员!'}
        elif request.args.get('access_token'):
            ext_token = request.args.get('access_token')
            print(ext_token)
            print(request.query_string)
            with db.get_connection(dba.dbn) as conn:
                where = {'name': ext_token}
                fields = 'id,name,name_cn'
                ext_info = conn.select_one(dba.user, where, fields)
                if ext_info:
                    self.cache9.hmset(ext_token, ext_info)
                    if self.find_privs(ext_info['id'], path, method):
                        return
            return {'code': 20403, 'msg': '用户权限不足, 请联系管理员!'}
        else:
            return {'code': 50014, 'msg': '用户Token过期, 请重新登录!'}
