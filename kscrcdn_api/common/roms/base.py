import time
import logging
import hashlib
import requests
import traceback
from datetime import datetime
from kscrcdn_api.config import settings

log = logging.getLogger()


class BaseRomsEvent:
    def __init__(self):
        pass

    @staticmethod
    def add_update(pk, items, cur_obj, pre_obj):
        incr_update = {pk: []}
        for char in items:
            if cur_obj.get(char) != pre_obj.get(char):
                incr_update[pk].append({
                    'current': cur_obj[char],
                    'previous': pre_obj[char]
                })
        if incr_update[pk]:
            return incr_update
        return {}

    @staticmethod
    def get_data_detail(char_map, cur_obj, pre_obj):
        update = {}
        for k, v in char_map.items():
            if k in cur_obj and (cur_obj.get(k) != pre_obj.get(k)):
                update[v] = {
                    'current': cur_obj[k],
                    'previous': pre_obj[k]
                }
        return update

    @staticmethod
    def get_save_body(**kwargs):
        now = datetime.now()
        local_time = datetime.strftime(now, '%Y-%m-%d %H:%M:%S')
        time_stamp = round(now.timestamp() * 1000)
        state_id = kwargs['stateId']
        txt = f"build + 0 + {state_id} + 1 + {time_stamp}"
        commit_id = hashlib.sha1(txt.encode("utf8")).hexdigest()  # c7b16c7c468cd413352500bdc9d032dd7e972aa7
        body = {
            "flowId": 0,
            "appId": "build",
            "userId": "rs_build",
            "lastStateId": 0,
            "orderType": "",
            "orderId": 0,
            "commitId": commit_id,
            "time": local_time,
            "timestamp": time_stamp
        }
        body.update(kwargs)
        return body

    def load_flow_id(self, node_group_id):
        """
        404: {'status': 404, 'message': '[没有数据] FlowHistory not found. flowTypeId: 541, flowVersion: 210601541, stateId: 541050500, relatedId: 2018082204'}
        """
        url = f'{settings.ROMS_DOMAIN}/api/v1/resource/load'
        data = {
            "read": {
                "route": "api/v1/flow",
                "field": [
                    "flowId",
                    "orderType",
                    "orderId"
                ]
            },
            "parameter": {
                "relatedId": node_group_id
            }
        }
        kwargs = dict(
            flow_type_id=541,
            flow_type='变更节点信息',
            flow_version=210601001,
            state_id=1030000,
            state='待建设',
            order_id=None,
            order_type=None
        )
        body = self.get_save_body(data, **kwargs)
        return self.post(url, body)

    def send(self):
        pass

    @staticmethod
    def post(url, data, headers={}):
        err = ''
        result = ''
        headers = headers or {'Content-Type': 'application/json; charset=UTF-8'}
        startm = time.perf_counter()
        try:
            res = requests.post(url, json=data, headers=headers)
            result = res.json()
        except Exception as e:
            log.error(traceback.format_exc())
            err = str(e)
        finally:
            endtm = time.perf_counter()
            log.info(f'func=roms_post|{url=}|{data=}|{result=}|time={int((endtm-startm)*1000000)}|{err=}')
        return result



if __name__ == '__main__':
    pass
    # roms = RomsEvent()
    # old_node = {'name': 'shpbs02', 'name_cn': '上海鹏博士02节点', 'node_idx': 2016081101}
    # new_node = {'name': 'shpbs02', 'name_cn': '上海鹏博士02节点xxx', 'node_idx': 2016081101}
    # print(roms.save_node_info(new_node, old_node))
