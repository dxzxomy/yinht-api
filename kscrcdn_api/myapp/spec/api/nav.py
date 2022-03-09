import logging
from flask import jsonify
from flask_restful import Resource, request
from kscrcdn_api.common import db
from kscrcdn_api.common import dbalias as dba
from pymysql.err import IntegrityError
import pandas as pd
import numpy as np

log = logging.getLogger()


class BaseNavAPI(Resource):
    default_fields = ['id', 'name', 'icon', 'url', 'level', 'pnode', 'utime', 'descr']

    # default_filter = ['a.node_id', 'a.username', 'a.vlan', 'd.sn', 'a.status']  # prerequest验证过滤条件合法性

    def get(self, nav_id, ecode=None, emsg=None):
        _fields = request.args.get('_fields', ','.join(self.default_fields))
        with db.get_connection(dba.dbn) as conn:
            dbdata = conn.select_one(dba.navi_list, {'id': nav_id}, _fields)
        if dbdata:
            code, msg = ecode or 20200, emsg or 'Got it!'
        else:
            code, msg = 20404, f'Not Found: {nav_id=}'
        return dict(code=code, msg=msg, data=dbdata)

    def put(self, nav_id):
        reqdata = request.json
        with db.get_connection(dba.dbn) as conn:
          conn.update(dba.navi_list, reqdata, {'id': nav_id})
        return self.get(nav_id, emsg='Updated!')

    def delete(self, nav_id):
        with db.get_connection(dba.dbn) as conn:
          dbdata = conn.delete(dba.navi_list, {'id': nav_id})
        if dbdata:
          return dict(code=20200, msg='Deleted!')
        return dict(code=20404, msg=f'Not found: {nav_id=}')


class NavListAPI(BaseNavAPI):

    def get(self):
        reqargs = request.args.to_dict()
        print(reqargs)
        _fields = reqargs.get('_fields', ','.join(self.default_fields))
        _filter = eval(reqargs.get('_filter', '{}'))
        limit = int(reqargs.get('limit', 10))
        page = int(reqargs.get('page', '1'))
        sort = reqargs.get('sort', '+id')
        desc = '' if sort == '+id' else 'desc'
        start_pos = 0 if page == 1 else f'{str((page - 1) * limit)}'
        other = f'order by id {desc} limit {start_pos}, {limit}'

        with db.get_connection(dba.dbn) as conn:
            count = conn.lselect_one(dba.navi_list, _filter, 'count(*)').get('count(*)')
            dbdata = conn.lselect(dba.navi_list, _filter, _fields, other)
            data = dict(total=count, items=dbdata)
        return dict(code=20200, data=data, msg='Got it!')
    
    
    def post(self):
        reqdata = request.json
        with db.get_connection(dba.dbn) as conn:
            name = reqdata['name']
            w = {'name': name}
            check = conn.select_one(dba.navi_list, w, 'id')
            if check:
                return dict(code=20408, msg=f'导航名称: {name} 已存在!')
            else:
                new_id = conn.insert(dba.navi_list, reqdata, 1)
        if new_id:
            return super(NavListAPI, self).get(new_id, 20201, 'Created!')
        return dict(code=20409, msg='Create failed! Please contact navi_list.')


class NavTreeList(BaseNavAPI):

    def get(self):
        reqargs = request.args.to_dict()
        _fields = reqargs.get('_fields', ','.join(self.default_fields))
        _filter = eval(reqargs.get('_filter', '{}'))
        limit = int(reqargs.get('limit', 10))
        page = int(reqargs.get('page', '1'))
        sort = reqargs.get('sort', '+id')
        desc = '' if sort == '+id' else 'desc'
        start_pos = 0 if page == 1 else f'{str((page - 1) * limit)}'
        other = f'order by id {desc} limit {start_pos}, {limit}'

        node_list = []
        node1_list = []
        with db.get_connection(dba.dbn) as conn:
            count = conn.select_one(dba.navi_list, _filter, 'count(*)').get('count(*)')
            nav_list = conn.select(dba.navi_list, fields=_fields)
            for nav in nav_list:
                if nav['level'] == 1:
                    node_list.append(nav)
                else:
                    node1_list.append(nav)

            for node in node_list:
                node.pop('url')
                node.update({'children': []})
                for node1 in node1_list:
                    if node['id'] == node1['pnode']:
                        node['children'].append(node1)
            data = dict(total=count, items=node_list)
        return dict(code=20200, data=data, msg='Got it!')

    def post(self):
        reqdata = request.json
        with db.get_connection(dba.dbn) as conn:
            new_id = conn.insert(dba.navi_list, reqdata, 1)
        if new_id:
            return super(NavTreeList, self).get(new_id, 20201, 'Created!')
        return dict(code=20409, emsg='Create failed! Please contact.')


class UploadAvatarAPI(Resource):
    
    def post(self):
        return dict(code=20200, msg='Success!')