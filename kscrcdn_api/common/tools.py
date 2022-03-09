import json
import logging
import traceback
import ipaddress
from kscrcdn_api.exceptions import MakePlanError
from kscrcdn_api.common import db
from kscrcdn_api.common import dbalias as dba
from kscrcdn_api.common.ndb import cache
from functools import cmp_to_key

log = logging.getLogger()


def is_json(raw_msg, default=None):
    try:
        load_msg = json.loads(raw_msg)
        return load_msg
    except:
        log.debug(f'Can not resovle json string {raw_msg}')
    if default is not None:
        return default
    else:
        return raw_msg

def with_json(raw_obj, default=None):
    try:
        dump_obj = json.dumps(raw_obj)
        return dump_obj
    except:
        log.debug(f'Can not dump json obj {raw_obj}')
    if default is not None:
        return default
    else:
        return raw_obj

def with_bool(raw_obj):
    return 1 if raw_obj else 0

def get_sql_other(filter_list, _filter):
    """
    filter_list = {
        ('status', 'status', 'in'),
        ('node_name', 'node_name', 'like'),
        ('cdn_order_type', 'cdn_order_type', '='),
        ('s_create_time', 'create_time', '>='),
        ('e_create_time', 'create_time', '<='),
        ('s_finish_time', 'finish_time', '>='),
        ('e_finish_time', 'finish_time', '<='),
    }
    :param _filter:
    :return:
    """
    other = ''
    if _filter:
        try:
            _filter = json.loads(_filter)
        except:
            _filter = eval(_filter)
        osql_list = []
        for ft in filter_list:
            osql_list.append(joinsql(_filter, *ft))
        osql_list = list(filter(lambda x: x, osql_list))
        other = ' and '.join(osql_list)
    return other and f'where {other}'

def joinsql(reqargs, field, char, sym):
    if sym == 'in':
        field_str = ''
        if reqargs.get(field):
            field_val = [str(i) for i in reqargs[field]]
            field_str = f'{char} {sym} ({",".join(field_val)})'
        return field_str
    elif sym == 'like':
        return reqargs.get(field, '') and f'{char} {sym} "{reqargs[field]}%"'
    else:
        return reqargs.get(field, '') and f'{char} {sym} "{reqargs[field]}"'

def get_sql_page(sort, page, limit):
    bol = sort[0] or '-'
    inx = sort[1:]
    sc = 'desc' if bol == '-' else ''
    limit_ql = f'order by {inx} {sc} ' \
               f'limit {int(limit)*(int(page)-1)}, {limit}'
    return limit_ql


def is_ipnetwork(val):
    val = str(val).strip()
    try:
        ipaddress.ip_network(val)
    except:
        val = False
    return val


def inttoip(num, sub=24):
    err = ''
    result = ''
    try:
        if is_ipnetwork(num):
            return num
        num = int(num)
        s = bin(num)[2:]
        s = s.zfill(32)
        g = []
        h = []
        for i in range(0, 32, 8):
            g.append(s[i:i+8])
        for temp in g:
            h.append(str(int(temp, 2)))
        result = '.'.join(h)
        return f'{result}/{sub}'
    except Exception as e:
        err = str(e)
        log.error(f'无效的整数: {num}, 无法转换为IP段')
        log.error(traceback.format_exc())
        raise MakePlanError(f'无效的内网IP块: {num}')
    finally:
        log.info(f'func=IntoIP|{num=}|{result=}|{err=}')


SEQ = ['relay', 'lvs', 'lcache', 'llive', 'cache', 'live']

def device_type_cmp(a, b):
    """按照类型排序"""
    s1, s2 = -1, -1
    if a.get('type') in SEQ:
        s1 = SEQ.index(a['type'])
    if b.get('type') in SEQ:
        s2 = SEQ.index(b['type'])
    return 1 if s1 > s2 else -1


def seq_server_list(server_list):
    server_list = sorted(server_list, key=lambda x: x['hostname'] or '', reverse=True)
    server_list = sorted(server_list, key=cmp_to_key(device_type_cmp))
    server_list = sorted(server_list, key=lambda x: x['node_id'] or 0)
    return server_list


def get_user_privs(user_id, conn=None, raw=False):
    fields = '`id`,`pid`,`name`,`type`,`route`,`path`,`limit`,`method`'
    sql = f'select {fields} from privileges where id in ' \
          f'(select privs_id from object_privs_rel where role_id in ' \
          f'(select role_id from user_role_rel where user_id={user_id}))'
    if conn:
        user_privs = conn.query(sql)
    else:
        with db.get_connection(dba.dbn) as conn:
            user_privs = conn.query(sql)
    if raw:
        view_privs = list(filter(lambda x: x['type'] == 'VIEW', user_privs))
    else:
        view_privs = [p['route'] for p in user_privs if p['type'] == 'VIEW']
    api_privs = list(filter(lambda x: x['type'] == 'API', user_privs))
    return view_privs, api_privs


def get_user_info_from_request(request):
    cookies = request.cookies.to_dict()
    rtree_token = cookies.get('rtree_token') or ''
    cache9 = cache(9)
    user_info = cache9.hgetall(rtree_token)
    return user_info


if __name__ == '__main__':
    print(inttoip(169751808))
