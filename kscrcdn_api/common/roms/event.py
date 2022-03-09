import logging
from kscrcdn_api.common.roms.base import BaseRomsEvent
from kscrcdn_api.config import settings

log = logging.getLogger()


class NodeChgToRoms(BaseRomsEvent):
    char_map = {
        'name_cn': 'zhName',
        'ipv6_supported': 'ipv6Supported',
        'ipv6_opened': 'ipv6Opened'
    }

    def save_node_info(self, node, old_node):
        url = f'{settings.ROMS_DOMAIN}/api/v1/resource/save'
        data = {
            "update": {},
            "parameter": {
                "enName": node['name'].lower(),
                "nodeGroupId": int(node['node_idx'] or 0)
            }
        }
        # char_list = self.char_map.values()
        update = self.get_data_detail(self.char_map, node, old_node)
        data['update'] = update
        if data['update'] and node['node_idx']:
            kwargs = dict(
                data=data,
                flowTypeId=541,
                flowType='变更节点信息',
                flowVersion=210601541,
                stateId=541050500,
                state='已变更',
            )
            body = self.get_save_body(**kwargs)
            return self.post(url, body)
        else:
            log.info(f'func=save_node_info|need_push=False|{node=}|{old_node=}')


class ServerChgToRoms(BaseRomsEvent):
    char_map = {
        'hostname': 'hostName',
        'rack': 'rack',
        'type': 'serverRole',
    }

    def save_server_info(self, server, old_server):
        url = f'{settings.ROMS_DOMAIN}/api/v1/resource/save'
        data = {
            "update": {},
            "parameter": {
                "sn": server['sn'],
            }
        }
        # char_list = self.char_map.values()
        update = self.get_data_detail(self.char_map, server, old_server)
        add_update = self.add_update('ips', ['out_ip', 'ilo_ip'], server, old_server)
        update.update(add_update)
        data['update'] = update
        if data['update'] and server['sn']:
            kwargs = dict(
                data=data,
                flowTypeId=542,
                flowType='变更服务器信息',
                flowVersion=210601542,
                stateId=542050500,
                state='已变更',
            )
            body = self.get_save_body(**kwargs)
            return self.post(url, body)
        else:
            log.info(f'func=save_server_info|need_push=False|{server=}|{old_server=}')


class SwitchChgToRoms(BaseRomsEvent):
    char_map = {
        'hostname': 'hostName',
        'rack': 'rack',
        'type': 'type',
    }

    def save_switch_info(self, switch, old_switch):
        url = f'{settings.ROMS_DOMAIN}/api/v1/resource/save'
        data = {
            "update": {},
            "parameter": {
                "sn": switch['sn'],
            }
        }
        # char_list = self.char_map.values()
        update = self.get_data_detail(self.char_map, switch, old_switch)
        add_update = self.add_update('ips', ['out_ip'], switch, old_switch)
        update.update(add_update)
        data['update'] = update
        if data['update'] and switch['sn']:
            kwargs = dict(
                data=data,
                flowTypeId=543,
                flowType='变更交换机信息',
                flowVersion=210601543,
                stateId=543050500,
                state='已变更',
            )
            body = self.get_save_body(**kwargs)
            return self.post(url, body)
        else:
            log.info(f'func=save_switch_info|need_push=False|{switch=}|{old_switch=}')


class UpperChgToRoms(BaseRomsEvent):
    char_map = {
        'switch_port': 'protId',
        'status': 'state'
    }

    def save_upper_info(self, upper, old_upper):
        url = f'{settings.ROMS_DOMAIN}/api/v1/resource/save'
        data = {
            "update": {},
            "parameter": {
                "switchSn": upper['switch_sn'],
                "portId": upper['switch_port'],
            }
        }
        # char_list = self.char_map.values()
        update = self.get_data_detail(self.char_map, upper, old_upper)
        data['update'] = update
        if data['update'] and upper['switch_sn'] and upper['switch_port']:
            kwargs = dict(
                data=data,
                flowTypeId=544,
                flowType='变更上联端口信息',
                flowVersion=210601543,
                stateId=543050500,
                state='已变更',
            )
            body = self.get_save_body(**kwargs)
            return self.post(url, body)
        else:
            log.info(f'func=save_upper_info|need_push=False|{upper=}|{old_upper=}')
