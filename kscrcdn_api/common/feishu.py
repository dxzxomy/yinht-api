import sys
import time
import json
import logging
import requests
import traceback
try:
    from kscrcdn_api.config import settings
except:
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    from kscrcdn_api.config import settings
log = logging.getLogger()
"""
飞书开发文档定制消息卡片：https://open.feishu.cn/document/ukTMukTMukTM/uczM3QjL3MzN04yNzcDN
Feishu Json Example

{
    "chat_id": 123 #机器人所在群的ID
    "msg_type": "interactive",
    "update_multi": False,
    "card": {
        # 标题
        "header": {
            "title": {
                "tag": "plain_text",
                "content": "标题文本",
            }
            template: 'red' # 标题颜色（选填）
        },
        # 内容
        "elements": [
            {
                "tag": "div",
                "text": {
                    "tag": "plain_text",
                    "content": "This is a very very very very very very very long text;"
                }
            }，
            {
                "tag": "action",
                "actions": [
                    {
                        "tag": "button",
                        "text": {
                            "tag": "plain_text",
                            "content": "Read"
                        },
                        "type": "default"
                    }
                ]
            }
        ]
    }
}
"""
class FeiShu:

    headers = {
        "Content-Type": "application/json; charset=utf-8"
    }

    def get_access_token(self):
        query = {
            "app_id": settings.APP_ID,
            "app_secret": settings.APP_SECRET
        }
        err = ''
        startm = time.perf_counter()
        result = ''
        try:
            res = requests.post(url=f'{settings.FEISHU_DOMAIN}/auth/v3/tenant_access_token/internal/', json=query,headers=self.headers)
            result = res.text
        except Exception as e:
            log.error(traceback.format_exc())
            err = str(e)
        finally:
            endtm = time.perf_counter()
            log.info(f'path=common.feishu|func=get_access_token|response={result}|time={int((endtm - startm) * 1000000)}|{err=}')
            return result

    # 获取机器人所在的群列表chat_id
    def get_chat_id(self):
        err = ''
        startm = time.perf_counter()
        result = ''
        try:
            access_token = self.get_access_token()
            if not access_token or not eval(access_token).get('code') == 0:
                log.error(f'path=common.feishu|func=get_access_token|response={access_token}')
                return
            access_token = eval(access_token)
            access_token = access_token.get('tenant_access_token')
            self.headers["Authorization"] = f"Bearer {access_token}"
            res = requests.get(url=f'{settings.FEISHU_DOMAIN}/chat/v4/list', headers=self.headers)
            result = res.text
        except Exception as e:
            log.error(traceback.format_exc())
            err = str(e)
        finally:
            endtm = time.perf_counter()
            log.info(f'path=common.feishu|func=get_chat_id|response={result}|time={int((endtm - startm) * 1000000)}|{err=}')
            return result


    def send_message(self, chatdict):
        err = ''
        startm = time.perf_counter()
        result = ''
        try:
            access_token = self.get_access_token()
            if access_token and eval(access_token).get('code') == 0:
                access_token = eval(access_token)
                access_token = access_token.get('tenant_access_token')
            chat = self.get_chat_id()
            chat_id = ''
            if chat:
                chat = json.loads(chat)
                groups = chat['data'].get('groups')[0]
                chat_id = groups.get('chat_id')
            self.headers['Authorization'] = f"Bearer {access_token}"
            chatdict['chat_id'] = chat_id
            query = chatdict
            res = requests.post(url=f'{settings.FEISHU_DOMAIN}/message/v4/send/', headers=self.headers, json=query)
            result = res.text
        except Exception as e:
            log.error(traceback.format_exc())
            err = str(e)
        finally:
            endtm = time.perf_counter()
            log.info(f'path=common.feishu|func=send_message|response={result}|time={int((endtm - startm) * 1000000)}|{err=}')
            return result

def install(feisdict):
    pyv = sys.version_info
    if pyv[0] == 2 and pyv[1] < 7:
        raise RuntimeError('python error, must python >= 2.7')
    if settings.FEISHU_OPEN == False:
        return 'OFF'
    header_title_content = feisdict.get('header-title', 'Notied')
    elements = []
    chatdict = {
        "msg_type": "interactive",
        "update_multi": False,
        "card": {
            "header": {
                "title": {
                    "tag": "plain_text",
                    "content": header_title_content
                }
            },
            "elements": elements
        }
    }
    if feisdict.get('div'):
        div_dict = {
            "tag": "div",
        }
        for div in feisdict.get('div'):
            if div.get('text'):
                text_data = div['text'][0].split('%')
                text_dict = {
                    "text": {
                        "tag": text_data[0],
                        "content": text_data[1]
                    }
                }
                div_dict.update(text_dict)
            if div.get('fields'):
                fields = []
                for field in div['fields']:
                    f = field.split('%')
                    is_short = False
                    if f[2] == 'True':
                        is_short = True
                    field_data = {
                      "is_short": is_short,
                      "text": {
                          "tag": f[0],
                          "content": f[1]
                      }
                    }
                    fields.append(field_data)
                div_dict.update({"fields": fields})
        elements.append(div_dict)
    return chatdict


def debug(msg, *args, **kwargs):
    if isinstance(msg, dict):
        chatdict = install(msg)
        if chatdict == 'OFF':
            return
        chatdict['card']['header']['template'] = 'bule'
        FeiShu().send_message(chatdict)

def warning(msg, *args, **kwargs):
    if isinstance(msg, dict):
        chatdict = install(msg)
        if chatdict == 'OFF':
            return
        chatdict['card']['header']['template'] = 'yellow'
        FeiShu().send_message(chatdict)


def info(msg, *args, **kwargs):
    if isinstance(msg, dict):
        chatdict = install(msg)
        if chatdict == 'OFF':
            return
        chatdict['card']['header']['template'] = 'green'
        FeiShu().send_message(chatdict)

def err(msg, *args, **kwargs):
    if isinstance(msg, dict):
        chatdict = install(msg)
        if chatdict == 'OFF':
            return
        chatdict['card']['header']['template'] = 'red'
        FeiShu().send_message(chatdict)

