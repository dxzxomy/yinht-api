from flask import request
from flask_restful import Resource
from kscrcdn_api.common import db
from kscrcdn_api.common import dbalias as dba
from kscrcdn_api.middleware.plugins import (UserTraceHandlerPlugin, UserAuthentication)
from kscrcdn_api.middleware.interceptor import (PreRequestWrapHandler, PostRequestWrapHandler)


class BaseUserAPI(Resource):

    method_decorators = {
        'get': [
            PreRequestWrapHandler([UserAuthentication], ),
        ],
        'put': [
            PostRequestWrapHandler([UserTraceHandlerPlugin], ),
            PreRequestWrapHandler([UserAuthentication], ),
        ],
        'delete': [
            PostRequestWrapHandler([UserTraceHandlerPlugin], ),
            PreRequestWrapHandler([UserAuthentication], ),
        ]
    }
    default_fields = [
        'u.id', 'u.name', 'u.name_cn', 'u.group_id', 'u.email', 'u.status', 'u.utime',
        'u.phone', 'r.name_cn as role_name', 'r.id as role_id'
    ]

    def agg_rel_data(self, dbdata):
        data = {}
        for v in dbdata:
            role = {}
            user_id = v['id']
            role_name = v.pop('role_name')
            role_id = v.pop('role_id')
            if role_name and role_id:
                role = {'role_name': role_name, 'role_id': role_id}
            if user_id not in data:
                data[user_id] = v
                data[user_id]['roles'] = []
            if role:
                data[user_id]['roles'].append(role)
        return list(data.values())

    def get(self, user_id, ecode=None, emsg=None):
        _fields = request.args.get('_fields', ','.join(self.default_fields))
        with db.get_connection(dba.dbn) as conn:
            sql = f'select {_fields} from {dba.user} as u left join {dba.user_role_rel} as urr on u.id=urr.user_id ' \
                  f'left join {dba.role} as r on urr.role_id=r.id where u.id={user_id};'
            dbdata = conn.query(sql)
            agg_data = self.agg_rel_data(dbdata)
            rsp_data = (agg_data or {}) and agg_data[0]
        if dbdata:
            code, msg = ecode or 20200, emsg or 'Got it!'
        else:
            code, msg = 20404, f'Not Found: {user_id=}'
        return dict(code=code, msg=msg, data=rsp_data)

    def put(self, user_id):
        reqdata = request.json
        roles = reqdata.pop('roles', [])
        with db.get_connection(dba.dbn) as conn:
            conn.update(dba.user, reqdata, {'id': user_id})
            rel_data = []
            for role in roles:
                rel_data.append({'user_id': user_id, 'role_id': role['role_id']})
            conn.delete(dba.user_role_rel, {'user_id': user_id})
            if rel_data:
                conn.insert_list(dba.user_role_rel, rel_data)
        return self.get(user_id, emsg='Updated!')

    def delete(self, user_id):
        with db.get_connection(dba.dbn) as conn:
            dbdata = conn.delete(dba.user, {'id': user_id})
        if dbdata:
            return dict(code=20200, msg='Deleted!')
        return dict(code=20404, msg=f'Not found: {user_id=}')


class UserListAPI(BaseUserAPI):
    method_decorators = {
        'get': [
            PreRequestWrapHandler([UserAuthentication], ),
        ],
        'post': [
            PostRequestWrapHandler([UserTraceHandlerPlugin], ),
            PreRequestWrapHandler([UserAuthentication], ),
        ]
    }

    def get(self):
        reqargs = request.args.to_dict()
        _fields = reqargs.get('_fields', ','.join(self.default_fields))
        _filter = eval(reqargs.get('_filter', '{}'))
        limit = int(reqargs.get('limit', 10))
        page = int(reqargs.get('page', '1'))
        sort = reqargs.get('sort', '+id')
        desc = '' if sort == '+id' else 'desc'
        start_pos = 0 if page == 1 else f'{str((page-1)*limit)}'
        other = f'order by u.id {desc} limit {start_pos}, {limit}'

        with db.get_connection(dba.dbn) as conn:
            count = conn.lselect_one(f'{dba.user} as u', _filter, 'count(*)').get('count(*)')
            where = conn.ldict2sql(_filter, ' and ')
            if where: where = f'where {where}'
            sql = f'select {_fields} from {dba.user} as u left join ' \
                  f'{dba.user_role_rel} as urr on u.id=urr.user_id ' \
                  f'left join {dba.role} as r on urr.role_id=r.id {where} {other};'
            dbdata = conn.query(sql)
            agg_data = self.agg_rel_data(dbdata)
            data = dict(total=count, items=agg_data)
        return dict(code=20200, data=data, msg='Got it!')

    def post(self):
        reqdata = request.json
        with db.get_connection(dba.dbn) as conn:
            new_id = conn.insert(dba.user, reqdata, 1)
        if new_id:
            return super(UserListAPI, self).get(new_id, 20201, 'Created!')
        return dict(code=20409, emsg='Create failed! Please contact administrator.')


class UserRoleRelAPI(Resource):

    method_decorators = {
        'put': [
            PostRequestWrapHandler([UserTraceHandlerPlugin], ),
            PreRequestWrapHandler([UserAuthentication], ),
        ]
    }

    def put(self, user_id):
        reqdata = request.json
        operator = reqdata.pop('operator')
        data = {'user_id': user_id, 'role_id': reqdata['role_id']}
        with db.get_connection(dba.dbn) as conn:
            if operator == 'add':
                if not conn.select_one(dba.user_role_rel, data, 'id'):
                    conn.insert(dba.user_role_rel, data)
                    return {'code': 20200, 'msg': 'success'}
            elif operator == 'del':
                conn.delete(dba.user_role_rel, data)
                return {'code': 20200, 'msg': 'success'}
        return {'code': 20202, 'msg': '条件不匹配'}
