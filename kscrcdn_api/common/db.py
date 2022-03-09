#!encoding: utf8
import time, datetime
import random
import threading
import logging
import traceback
from contextlib import contextmanager

log = logging.getLogger()

dbpool = None

settings = {
    # 是否格式化time结尾的字段为datetime类型
    'format_time': False,
    # 日志级别 all/simple
    'log_level': 'all',
}


def timeit(func):
    def _(*args, **kwargs):
        starttm = time.time()
        ret = 0
        num = 0
        err = ''
        try:
            retval = func(*args, **kwargs)
            if isinstance(retval, list):
                num = len(retval)
            elif isinstance(retval, dict):
                num = 1
            elif isinstance(retval, int):
                ret = retval
            return retval
        except Exception as e:
            err = e
            ret = -1
            raise
        finally:
            endtm = time.time()
            conn = args[0]
            # dbcf = conn.pool.dbcf
            dbcf = conn.param
            sql = repr(args[1])
            if settings.get('log_level', 'all') == 'simple':
                sql = sql.split()[0].strip("'")
            log.info(
                'server=%s|id=%d|name=%s|system=%s|r=%s|addr=%s:%d|db=%s|c=%d,%d,%d|tr=%d|time=%d|ret=%s|n=%d|sql=%s|err=%s',
                conn.type, int(conn.conn_id) % 10000,
                conn.name, dbcf.get('system', ''), conn.role,
                dbcf.get('host', ''), dbcf.get('port', 0),
                dbcf.get('db', ''),
                len(conn.pool.dbconn_idle),
                len(conn.pool.dbconn_using),
                conn.pool.max_conn, conn.trans,
                int((endtm - starttm) * 1000000),
                str(ret), num,
                sql, err)

    return _


class DBPoolBase:
    def acquire(self, name):
        pass

    def release(self, name, conn):
        pass


class DBResult:
    def __init__(self, fields, data):
        self.fields = fields
        self.data = data

    def todict(self):
        ret = []
        for item in self.data:
            ret.append(dict(zip(self.fields, item)))
        return ret

    def __iter__(self):
        for row in self.data:
            yield dict(zip(self.fields, row))

    def row(self, i, isdict=True):
        if isdict:
            return dict(zip(self.fields, self.data[i]))
        return self.data[i]

    def __getitem__(self, i):
        return dict(zip(self.fields, self.data[i]))


class DBFunc:
    def __init__(self, data):
        self.value = data


class DBConnection:
    def __init__(self, param, lasttime, status):
        self.name = param.get('name')
        self.param = param
        self.conn = None
        self.status = status
        self.lasttime = lasttime
        self.pool = None
        self.server_id = None
        self.conn_id = 0
        self.trans = 0  # is start transaction
        self.role = param.get('role', 'm')  # master/slave

    def __str__(self):
        return '<%s %s:%d %s@%s>' % (self.type,
                                     self.param.get('host', ''), self.param.get('port', 0),
                                     self.param.get('system', ''), self.param.get('db', 0)
                                     )

    def is_available(self):
        return self.status == 0

    def useit(self):
        self.status = 1
        self.lasttime = time.time()

    def releaseit(self):
        self.status = 0

    def connect(self):
        pass

    def close(self):
        pass

    def alive(self):
        pass

    def cursor(self):
        return self.conn.cursor()

    @timeit
    def execute(self, sql, lastid=0, param=None):
        # log.info('exec:%s', sql)
        cur = self.conn.cursor()
        if param:
            ret = cur.execute(sql, param)
        else:
            ret = cur.execute(sql)
        if lastid:
            ret = int(cur.lastrowid)
        cur.close()
        return ret

    @timeit
    def executemany(self, sql, param=None):
        cur = self.conn.cursor()
        ret = cur.executemany(sql, param)
        cur.close()
        return ret

    @timeit
    def query(self, sql, param=None, isdict=True, head=False):
        '''sql查询，返回查询结果'''
        # log.info('query:%s', sql)
        cur = self.conn.cursor()
        if param:
            cur.execute(sql, param)
        else:
            cur.execute(sql)
        res = cur.fetchall()
        cur.close()
        res = [self.format_timestamp(r, cur) for r in res]
        if res and isdict:
            ret = []
            xkeys = [i[0] for i in cur.description]
            for item in res:
                one = dict(zip(xkeys, item))
                ret.append(one)
        else:
            ret = res
            if head:
                xkeys = [i[0] for i in cur.description]
                ret.insert(0, xkeys)
        return ret

    @timeit
    def get(self, sql, param=None, isdict=True):
        '''sql查询，只返回一条'''
        cur = self.conn.cursor()
        cur.execute(sql, param)
        res = cur.fetchone()
        cur.close()
        res = self.format_timestamp(res, cur)
        if res and isdict:
            xkeys = [i[0] for i in cur.description]
            one = dict(zip(xkeys, res))
            return one
        else:
            return res or {}

    def field2sql(self, v, charset='utf-8'):
        if isinstance(v, bytes):
            v = v.decode(charset)

        return self.escape(v)

    def value2sql(self, v, charset='utf-8'):
        if isinstance(v, bytes):
            v = v.decode(charset)

        if isinstance(v, str):
            if v.startswith(('now()', 'md5(')):
                return v
            return "'%s'" % self.escape(v)
        elif isinstance(v, datetime.datetime) or isinstance(v, datetime.date):
            return "'%s'" % str(v)
        elif isinstance(v, DBFunc):
            return v.value
        else:
            if v is None:
                return 'NULL'
            return str(v)

    def exp2sql(self, key, op, value):
        item = '(`%s` %s ' % (key.strip('`').replace('.', '`.`'), op)
        if op == 'in':
            item += '(%s))' % ','.join([self.value2sql(x) for x in value])
        elif op == 'not in':
            item += '(%s))' % ','.join([self.value2sql(x) for x in value])
        elif op == 'between':
            item += ' %s and %s)' % (self.value2sql(value[0]), self.value2sql(value[1]))
        else:
            item += self.value2sql(value) + ')'
        return item

    def dict2sql(self, d, sp=','):
        """字典可以是 {name:value} 形式，也可以是 {name:(operator, value)}"""
        x = []
        for k, v in d.items():
            if isinstance(v, (tuple, list)):
                x.append('%s' % self.exp2sql(k, v[0], v[1]))
            else:
                x.append('`%s`=%s' % (k.strip(' `').replace('.', '`.`'), self.value2sql(v)))
        return sp.join(x)

    def ldict2sql(self, d, sp=','):
        """字典可以是 {name:value} 形式，也可以是 {name:(operator, value)}"""
        x = []
        for k, v in d.items():
            if isinstance(v, (tuple, list)):
                x.append('%s' % self.exp2sql(k, v[0], v[1]))
            else:
                if 'id' in k and isinstance(v, int):
                    v = str(v)
                else:
                    v = f'{v}%'
                x.append(f'`{k.strip(" `").replace(".", "`.`")}` like {self.value2sql(v)}')
        return sp.join(x)

    def dict2on(self, d, sp=' and '):
        x = []
        for k, v in d.items():
            x.append('`%s`=`%s`' % (k.strip(' `').replace('.', '`.`'), v.strip(' `').replace('.', '`.`')))
        return sp.join(x)

    def dict2insert(self, d):
        keys = list(d.keys())
        keys.sort()
        vals = []
        for k in keys:
            vals.append('%s' % self.value2sql(d[k]))
        new_keys = ['`' + k.strip('`') + '`' for k in keys]
        return ','.join(new_keys), ','.join(vals)

    def fields2where(self, fields, where=None):
        if not where:
            where = {}
        for f in fields:
            if f.value == None or (f.value == '' and f.must):
                continue
            where[f.name] = (f.op, f.value)
        return where

    def format_table(self, table):
        """调整table 支持加上 `` 并支持as"""
        table = table.strip(' `').replace(',', '`,`')
        index = table.find(' ')
        if ' ' in table:
            return '`%s`%s' % (table[:index], table[index:])
        else:
            return '`%s`' % table

    def select_sql(self, table, where=None, fields='*', other=None):
        if isinstance(fields, (list, tuple)):
            fields = ','.join([self.field2sql(x) for x in fields])
        else:
            fields = ','.join([self.field2sql(x) for x in fields.split(',')])

        sql = "select %s from %s" % (fields, self.format_table(table))
        if where:
            sql += " where %s" % self.dict2sql(where, ' and ')
        if other:
            sql += ' ' + other
        return sql

    def lselect_sql(self, table, where=None, fields='*', other=None):
        if isinstance(fields, (list, tuple)):
            fields = ','.join([self.field2sql(x) for x in fields])
        else:
            fields = ','.join([self.field2sql(x) for x in fields.split(',')])

        sql = "select %s from %s" % (fields, self.format_table(table))
        if where:
            sql += " where %s" % self.ldict2sql(where, ' and ')
        if other:
            sql += ' ' + other
        return sql

    def select_join_sql(self, table1, table2, join_type='inner', on=None, where=None, fields='*', other=None):
        if isinstance(fields, (list, tuple)):
            fields = ','.join([self.field2sql(x) for x in fields])
        else:
            fields = ','.join([self.field2sql(x) for x in fields.split(',')])

        sql = "select %s from %s %s join %s" % (fields, self.format_table(table1), join_type, self.format_table(table2))
        if on:
            sql += " on %s" % self.dict2on(on, ' and ')
        if where:
            sql += " where %s" % self.dict2sql(where, ' and ')
        if other:
            sql += ' ' + other
        return sql

    def lselect_join_sql(self, table1, table2, join_type='inner', on=None, where=None, fields='*', other=None):
        if isinstance(fields, (list, tuple)):
            fields = ','.join([self.field2sql(x) for x in fields])
        else:
            fields = ','.join([self.field2sql(x) for x in fields.split(',')])

        sql = "select %s from %s %s join %s" % (fields, self.format_table(table1), join_type, self.format_table(table2))
        if on:
            sql += " on %s" % self.dict2on(on, ' and ')
        if where:
            sql += " where %s" % self.ldict2sql(where, ' and ')
        if other:
            sql += ' ' + other
        return sql

    def last_insert_id(self):
        pass

    def start(self):  # start transaction
        self.trans = 1
        pass

    def commit(self):
        self.trans = 0
        self.conn.commit()

    def rollback(self):
        self.trans = 0
        self.conn.rollback()

    def escape(self, s):
        return s

    def format_timestamp(self, ret, cur):
        index = []
        if cur.description:
            for d in cur.description:
                if d[0].endswith('time'):
                    index.append(cur.description.index(d))

        res = []
        if ret:
            for i, t in enumerate(ret):
                if i in index and isinstance(t, datetime.datetime):
                    rtime = t.strftime("%Y-%m-%d %H:%M:%S")
                    res.append(rtime)
                else:
                    res.append(t)
        return res


def with_mysql_reconnect(func):
    def close_mysql_conn(self):
        log.info('close conn:%s', self.conn)
        try:
            self.conn.close()
        except:
            log.warning(traceback.format_exc())
            self.conn = None

    def _(self, *args, **argitems):
        if self.type == 'mysql':
            import MySQLdb as m
        elif self.type == 'pymysql':
            import pymysql as m
        trycount = 3
        while True:
            try:
                x = func(self, *args, **argitems)
            except m.OperationalError as e:
                log.warning(traceback.format_exc())
                if e.args[0] >= 2000 and self.trans == 0:  # 连接断开错误
                    close_mysql_conn(self)
                    self.connect()
                    trycount -= 1
                    if trycount > 0:
                        continue
                raise
            except (m.InterfaceError, m.InternalError) as e:
                # FIXME: 有时候InternalError错误不需要断开数据库连接，比如表不存在的错误
                log.warning(traceback.format_exc())
                if self.trans == 0:  # 连接断开错误
                    close_mysql_conn(self)
                    self.connect()
                    trycount -= 1
                    if trycount > 0:
                        continue
                raise
            else:
                return x

    return _


class PyMySQLConnection(DBConnection):
    type = "pymysql"

    def __init__(self, param, lasttime, status):
        super(PyMySQLConnection, self).__init__(param, lasttime, status)
        self.connect()

    def connect(self):
        engine = self.param['engine']
        if engine == 'pymysql':
            import pymysql
            self.conn = pymysql.connect(host=self.param['host'],
                                        port=self.param['port'],
                                        user=self.param['system'],
                                        passwd=self.param['passwd'],
                                        db=self.param['db'],
                                        charset=self.param['charset'],
                                        connect_timeout=self.param.get('timeout', 10),
                                        )
            self.conn.autocommit(1)
            self.trans = 0

            cur = self.conn.cursor()
            cur.execute("show variables like 'server_id'")
            row = cur.fetchone()
            self.server_id = int(row[1])
            cur.close()

            cur = self.conn.cursor()
            cur.execute("select connection_id()")
            row = cur.fetchone()
            self.conn_id = row[0]
            cur.close()
        else:
            raise ValueError('engine error:' + engine)
        log.info('server=%s|func=connect|id=%d|name=%s|system=%s|role=%s|addr=%s:%d|db=%s',
                 self.type, self.conn_id % 10000,
                 self.name, self.param.get('system', ''), self.role,
                 self.param.get('host', ''), self.param.get('port', 0),
                 self.param.get('db', ''))

    @timeit
    def trans_execute(self, sqls):
        self.conn.begin()
        cur = self.conn.cursor()
        try:
            self.trans = 1
            for sql in sqls:
                print(cur.execute(sql))
        except Exception as e:
            log.error(traceback.format_exc(e))
            self.conn.rollback()  # 事务回滚
            print('事务处理失败', e)
        else:
            self.conn.commit()  # 事务提交
            print('事务处理成功', cur.rowcount)  # 关闭连接
            cur.close()
            self.conn.close()
        self.trans = 0

    def useit(self):
        self.status = 1
        self.lasttime = time.time()

    def releaseit(self):
        self.status = 0

    def close(self):
        log.info('server=%s|func=close|id=%d', self.type, self.conn_id % 10000)
        self.conn.close()
        self.conn = None

    @with_mysql_reconnect
    def alive(self):
        if self.is_available():
            cur = self.conn.cursor()
            cur.execute("show tables;")
            cur.close()
            self.conn.ping()

    @with_mysql_reconnect
    def execute(self, sql, param=None):
        return DBConnection.execute(self, sql, param)

    @with_mysql_reconnect
    def executemany(self, sql, param):
        return DBConnection.executemany(self, sql, param)

    @with_mysql_reconnect
    def query(self, sql, param=None, isdict=True, head=False):
        return DBConnection.query(self, sql, param, isdict, head)

    @with_mysql_reconnect
    def get(self, sql, param=None, isdict=True):
        return DBConnection.get(self, sql, param, isdict)

    def escape(self, s, enc='utf-8'):
        ns = self.conn.escape_string(s)
        return ns

    def last_insert_id(self):
        ret = self.query('select last_insert_id()', isdict=False)
        return ret[0][0]

    def start(self):
        self.trans = 1
        sql = "start transaction"
        return self.execute(sql)

    def commit(self):
        self.trans = 0
        sql = 'commit'
        return self.execute(sql)

    def rollback(self):
        self.trans = 0
        sql = 'rollback'
        return self.execute(sql)

    def insert(self, table, values, lastid=0, other=None):
        keys, vals = self.dict2insert(values)
        sql = "insert into %s(%s) values (%s)" % (self.format_table(table), keys, vals)
        if other:
            sql += ' ' + other
        return self.execute(sql, lastid)

    def insert_list(self, table, values_list, other=None):
        sql = 'insert into %s ' % self.format_table(table)
        sql_key = ''
        sql_value = []
        for values in values_list:
            keys, vals = self.dict2insert(values)
            sql_key = keys  # 正常key肯定是一样的
            sql_value.append('(%s)' % vals)
        sql += ' (' + sql_key + ') ' + 'values' + ','.join(sql_value)
        if other:
            sql += ' ' + other
        return self.execute(sql)

    def update(self, table, values, where=None, other=None):
        sql = "update %s set %s" % (self.format_table(table), self.dict2sql(values))
        if where:
            sql += " where %s" % self.dict2sql(where, ' and ')
        if other:
            sql += ' ' + other
        return self.execute(sql)

    def delete(self, table, where, other=None):
        sql = "delete from %s" % self.format_table(table)
        if where:
            sql += " where %s" % self.dict2sql(where, ' and ')
        if other:
            sql += ' ' + other
        return self.execute(sql)

    def select(self, table, where=None, fields='*', other=None, isdict=True):
        sql = self.select_sql(table, where, fields, other)
        return self.query(sql, None, isdict=isdict)

    def lselect(self, table, where=None, fields='*', other=None, isdict=True):
        sql = self.lselect_sql(table, where, fields, other)
        return self.query(sql, None, isdict=isdict)

    def select_one(self, table, where=None, fields='*', other=None, isdict=True):
        if not other:
            other = ' limit 1'
        if 'limit' not in other:
            other += ' limit 1'
        sql = self.select_sql(table, where, fields, other)
        return self.get(sql, None, isdict=isdict)

    def lselect_one(self, table, where=None, fields='*', other=None, isdict=True):
        if not other:
            other = ' limit 1'
        if 'limit' not in other:
            other += ' limit 1'
        sql = self.lselect_sql(table, where, fields, other)
        return self.get(sql, None, isdict=isdict)

    def select_join(self, table1, table2, join_type='inner', on=None, where=None, fields='*', other=None, isdict=True):
        sql = self.select_join_sql(table1, table2, join_type, on, where, fields, other)
        return self.query(sql, None, isdict=isdict)

    def lselect_join(self, table1, table2, join_type='inner', on=None, where=None, fields='*', other=None, isdict=True):
        sql = self.lselect_join_sql(table1, table2, join_type, on, where, fields, other)
        return self.query(sql, None, isdict=isdict)

    def select_join_one(self, table1, table2, join_type='inner', on=None, where=None, fields='*', other=None,
                        isdict=True):
        if not other:
            other = ' limit 1'
        if 'limit' not in other:
            other += ' limit 1'
        sql = self.select_join_sql(table1, table2, join_type, on, where, fields, other)
        return self.get(sql, None, isdict=isdict)

    def lselect_join_one(self, table1, table2, join_type='inner', on=None, where=None, fields='*', other=None,
                        isdict=True):
        if not other:
            other = ' limit 1'
        if 'limit' not in other:
            other += ' limit 1'
        sql = self.lselect_join_sql(table1, table2, join_type, on, where, fields, other)
        return self.get(sql, None, isdict=isdict)


class DBPool(DBPoolBase):
    def __init__(self, dbcf):
        # one item: [conn, last_get_time, stauts]
        self.dbconn_idle = []
        self.dbconn_using = []

        self.dbcf = dbcf
        self.max_conn = 20
        self.min_conn = 1

        if 'conn' in self.dbcf:
            self.max_conn = self.dbcf['conn']

        self.connection_class = {}
        x = globals()
        for v in x.values():
            if isinstance(v, type) and v != DBConnection and issubclass(v, DBConnection):
                self.connection_class[v.type] = v

        self.lock = threading.Lock()
        self.cond = threading.Condition(self.lock)

        self.open(self.min_conn)

    def synchronize(func):
        def _(self, *args, **argitems):
            self.lock.acquire()
            x = None
            try:
                x = func(self, *args, **argitems)
            finally:
                self.lock.release()
            return x

        return _

    def open(self, n=1):
        param = self.dbcf
        newconns = []
        for i in range(0, n):
            myconn = self.connection_class[param['engine']](param, time.time(), 0)
            myconn.pool = self
            newconns.append(myconn)
        self.dbconn_idle += newconns

    def clear_timeout(self):
        now = time.time()
        dels = []
        allconn = len(self.dbconn_idle) + len(self.dbconn_using)
        for c in self.dbconn_idle:
            if allconn == 1:
                break
            if now - c.lasttime > self.dbcf.get('idle_timeout', 10):
                dels.append(c)
                allconn -= 1

        if dels:
            log.debug('close timeout db conn:%d', len(dels))
        for c in dels:
            if c.conn:
                c.close()
            self.dbconn_idle.remove(c)

    @synchronize
    def acquire(self, timeout=10):
        start = time.time()
        while len(self.dbconn_idle) == 0:
            if len(self.dbconn_idle) + len(self.dbconn_using) < self.max_conn:
                self.open()
                continue
            self.cond.wait(timeout)
            if int(time.time() - start) > timeout:
                log.error('func=acquire|error=no idle connections')
                raise RuntimeError('no idle connections')

        conn = self.dbconn_idle.pop(0)
        conn.useit()
        self.dbconn_using.append(conn)

        if random.randint(0, 100) > 80:
            try:
                self.clear_timeout()
            except:
                log.error(traceback.format_exc())

        return conn

    @synchronize
    def release(self, conn):
        if conn:
            if conn.trans:
                log.debug('realse close conn use transaction')
                conn.close()
                # conn.connect()

            self.dbconn_using.remove(conn)
            conn.releaseit()
            if conn.conn:
                self.dbconn_idle.insert(0, conn)
        self.cond.notify()

    @synchronize
    def alive(self):
        for conn in self.dbconn_idle:
            conn.alive()

    def size(self):
        return len(self.dbconn_idle), len(self.dbconn_using)


class DBConnProxy:
    def __init__(self, pool, timeout=10):
        self._pool = pool
        self._master = None
        self._slave = None
        self._timeout = timeout

        self._modify_methods = set(['execute', 'executemany', 'last_insert_id',
                                    'insert', 'update', 'delete', 'insert_list', 'start', 'rollback', 'commit'])

    def __getattr__(self, name):
        if name in self._modify_methods:
            if not self._master:
                self._master = self._pool.master.acquire(self._timeout)
            return getattr(self._master, name)
        else:
            if name == 'master':
                if not self._master:
                    self._master = self._pool.master.acquire(self._timeout)
                return self._master
            if name == 'slave':
                if not self._slave:
                    self._slave = self._pool.get_slave().acquire(self._timeout)
                return self._slave

            if not self._slave:
                self._slave = self._pool.get_slave().acquire(self._timeout)
            return getattr(self._slave, name)


class RWDBPool:
    def __init__(self, dbcf):
        self.dbcf = dbcf
        self.name = ''
        self.policy = dbcf.get('policy', 'round_robin')

        master_cf = dbcf.get('master', None)
        master_cf['name'] = dbcf.get('name', '')
        master_cf['role'] = 'm'
        self.master = DBPool(master_cf)

        self.slaves = []

        self._slave_current = -1

        for x in dbcf.get('slave', []):
            x['name'] = dbcf.get('name', '')
            x['role'] = 's'
            slave = DBPool(x)
            self.slaves.append(slave)

    def get_slave(self):
        if self.policy == 'round_robin':
            size = len(self.slaves)
            self._slave_current = (self._slave_current + 1) % size
            return self.slaves[self._slave_current]
        else:
            raise ValueError('policy not support')

    def get_master(self):
        return self.master

    def acquire(self, timeout=10):
        return DBConnProxy(self, timeout)

    def release(self, conn):
        if conn._master:
            conn._master.pool.release(conn._master)
        if conn._slave:
            conn._slave.pool.release(conn._slave)

    def size(self):
        ret = {'master': (-1, -1), 'slave': []}
        if self.master:
            x = self.master
            key = '%s@%s:%d' % (x.dbcf['system'], x.dbcf['host'], x.dbcf['port'])
            ret['master'] = (key, self.master.size())
        for x in self.slaves:
            key = '%s@%s:%d' % (x.dbcf['system'], x.dbcf['host'], x.dbcf['port'])
            ret['slave'].append((key, x.size()))
        return ret


def checkalive(name=None):
    global dbpool
    while True:
        if name is None:
            checknames = dbpool.keys()
        else:
            checknames = [name]
        for k in checknames:
            pool = dbpool[k]
            pool.alive()
        time.sleep(300)


def install(cf):
    global dbpool
    if dbpool:
        log.warning("too many install db")
        return dbpool
    dbpool = {}

    for name, item in cf.items():
        item['name'] = name
        dbp = None
        if 'master' in item:
            dbp = RWDBPool(item)
        else:
            dbp = DBPool(item)
        dbpool[name] = dbp
    return dbpool


def acquire(name, timeout=10):
    global dbpool
    # log.info("acquire:", name)
    pool = dbpool[name]
    x = pool.acquire(timeout)
    x.name = name
    return x


def release(conn):
    if not conn:
        return
    global dbpool
    # log.info("release:", name)
    pool = dbpool[conn.name]
    return pool.release(conn)


# 推荐使用的获取数据库连接的方法
@contextmanager
def get_connection(token):
    conn = None
    try:
        conn = acquire(token)
        yield conn
    except:
        log.error("error=%s", traceback.format_exc())
        raise
    finally:
        if conn:
            release(conn)


get_connection_exception = get_connection


@contextmanager
def get_connection_noexcept(token):
    conn = None
    try:
        conn = acquire(token)
        yield conn
    except:
        log.error("error=%s", traceback.format_exc())
    finally:
        if conn:
            release(conn)


# 只能用在类方法上面，并且并不推荐使用此方法，使用get_connection更好
def with_database(name, errfunc=None, errstr=''):
    def f(func):
        def _(self, *args, **argitems):
            self.db = acquire(name)
            x = None
            try:
                x = func(self, *args, **argitems)
            except:
                if errfunc:
                    return getattr(self, errfunc)(error=errstr)
                else:
                    raise
            finally:
                release(self.db)
            return x

        return _

    return f


