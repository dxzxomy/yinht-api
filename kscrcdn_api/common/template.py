# coding: utf-8
import sys
import time
import json
import jinja2
import traceback
from datetime import datetime
import logging
try:
    from kscrcdn_api.common import db, logger, feishu
    from kscrcdn_api.common import dbalias as dba
    from kscrcdn_api.config import settings
except:
    print(traceback.format_exc())
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from kscrcdn_api.common import db, logger, feishu
    from kscrcdn_api.common import dbalias as dba
    from kscrcdn_api.config import settings

log = logging.getLogger()

class Template:

    @staticmethod
    def to_switch(data, opt):
        """
        生成交换机配置模板
        :param data: 交换机数据
        :param opt: 任务类型
        :return:
        """
        model = []
        err = ''
        startm = time.perf_counter()
        result = ''
        name = ''
        try:
            with db.get_connection(dba.dbn) as conn:
                task = conn.select_one(dba.task, {'name': opt}, fields="id")
            task_id = task.get('id')
            if 'RUIJIE' in data['model']:
                if data['model'] not in model:
                    if data['type'] in ['out', 'core']:
                        name = 'RUIJIE-OUT-BASE'
                    if data['type'] == 'in':
                        name = 'RUIJIE-IN-BASE'
                    if data['type'] == 'mgt':
                        name = 'RUIJIE-MG-BASE'
                else:
                    return
            # if 'H3C' in temp_data['model']:
            #     return
            # if 'HUAWeI' in temp_data['model']:
            #     return
            template = conn.select_one(dba.sw_tmpl, {'task_id': task_id, 'name': name}, fields='content')
            if template:
                result = dict(content=template['content'])
        except Exception as e:
            err = str(e)
            log.error(f'path=common.template|class=Template|fun=to_switch|err={traceback.format_exc()}')
        finally:
            endtm = time.perf_counter()
            log.info(f'path=kscrcdn_api.common|class=Template|func=to_switch|{opt=}|{name=}|{data=}|time={int((endtm - startm) * 1000000)}|{err=}')
            return result

    @staticmethod
    def to_server(data):
        return

def init(item):
    """
    初始化noc数据
    :param item: noc数据
    :return:
    """
    noc = item.get('noc')
    data = item.get('data')
    ulist = []
    node_list = noc['node_list']
    upper_list = noc['new_upper_list'] + noc['upper_list']
    switch_list = noc['new_switch_list'] + noc['switch_list']
    server_list = noc['new_server_list'] + noc['server_list']
    for switch in switch_list:
        if data['sn'] == switch['sn']:
            for upper in upper_list:
                if switch['sn'] == ['upper.switch_sn']:
                    ulist.append(upper)
            data['upper_list'] = ulist
            for node in node_list:
                if switch['node_id'] == node['id']:
                    isp = node['isp']
                    ext = node['ext']
                    data['in_gw'] = ext['in_gw']
                    data['in_mask'] = ext['in_netmask']
                    data['mgt_gw'] = ext['ilo_gw']
                    data['mgt_mask'] = ext['ilo_netmask']
                    data['ip_block'] = isp[0]['ip_block']
            sp1 = []
            sp2 = []
            for server in server_list:
                switch_port1 = server['switch_port1']
                if switch_port1['sn'] == switch['sn']:
                    sp1.append(switch_port1['port'])
                switch_port2 = server['switch_port2']
                if switch_port2['sn'] == switch['sn']:
                    sp2.append(switch_port2['port'])
            data['switch_port1'] = sp1
            data['switch_port2'] = sp2
    return data



def install(item):
    try:
        type = item['type']
        option = item['option']
        template = getattr(Template, f'to_{type}')
        data = init(item)
        temp = template(data, option)
        if not isinstance(temp, dict):
            return temp
        jinja2_tmpl = jinja2.Template(source=temp['content'])
        result = jinja2_tmpl.render(data={'data': data})
        rlist = list(map(lambda x: x.lstrip(), result.split('\n')))
        while '' in rlist:
            rlist.remove('')
        ret = "\n".join(rlist)
        temp_file = f"{data.get('hostname')}"
        return dict(name=temp_file, data=ret)
    except Exception as e:
        log.error(f"path=kscrcdn_api.common|func=install|err={traceback.format_exc()}")
        return str(e)
