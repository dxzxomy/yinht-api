import time
import requests
import logging
import traceback
from kscrcdn_api.config.settings import CAP_DOMAIN, CAP_SECRET

log = logging.getLogger()


class CapacityInfo:
    def __init__(self):
        pass

    def request(self, func, url, payload, headers=None):
        if not headers:
            headers = {
                'Accept': 'application/json, text/plain, */*',
                'Content-Type': 'application/json;charset=UTF-8',
            }
        stm = time.perf_counter()
        err, r = None, None
        try:
            r = func(url, headers=headers, json=payload)
            r = r.json()
        except Exception as e:
            err = str(e)
            log.error(traceback.format_exc())
        finally:
            etm = time.perf_counter()
            log.info(f'func=CapacityInfo|{url=}|{payload=}|{headers=}|{r=}|time={int((etm-stm)*1000000)}|err={err}')
            # print(f'func=CapacityInfo|{url=}|{payload=}|{headers=}|{r=}|time={int((etm - stm) * 1000000)}|err={err}')
        return r

    def get_token(self):
        url = f'{CAP_DOMAIN}/api/v2/getAccessToken'
        payload = {"id": 25, "secret": CAP_SECRET}
        response = self.request(requests.post, url, payload)
        if response.get('result'):
            return response['result']

    def get_node_resource(self, node_idx):
        url = f'{CAP_DOMAIN}/api/v1/capacity/getNodeDeployInfo'
        payload = {'nodeId': node_idx}
        token = self.get_token()
        if token:
            headers = {'Content-Type': 'application/json', 'Cookie': f'ksc_digest={token}'}
            response = self.request(requests.post, url, payload, headers)
            if response and response.get('result'):
                return response['result'][0]['resourceType']


if __name__ == '__main__':
    c = CapacityInfo()
    # print(c.get_token())
    print(c.get_node_resource('2021111503'))
