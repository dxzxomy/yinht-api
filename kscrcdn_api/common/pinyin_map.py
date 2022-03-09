city = {
}

isp = {
    'UN': {
        'name_zh': '联通',
        'abb_upper': 'UN',
    },
    'CT': {
        'name_zh': '电信',
        'abb_upper': 'CT',
    },
    'CM': {
        'name_zh': '移动',
        'abb_upper': 'CM',
    },
    'OC': {
        'name_zh': '广电',
        'abb_upper': 'OC',
    },
    'MP': {
        'name_zh': '多线',
        'abb_upper': 'MP',
    },
    'CTT': {
        'name_zh': '铁通',
        'abb_upper': 'CTT',
    },
    'PBS': {
        'name_zh': '鹏博士',
        'abb_upper': 'PBS',
    },
    'HK': {
        'name_zh': '浩宽',
        'abb_upper': 'HK',
    },
    'FD': {
        'name_zh': '方正',
        'abb_upper': 'FD',
    },
    'KP': {
        'name_zh': '宽频',
        'abb_upper': 'KP',
    },
    'WASU': {
        'name_zh': '华数',
        'abb_upper': 'WASU',
    },
    'BGP': {
        'name_zh': 'BGP',
        'abb_upper': 'BGP',
    },
    'CE': {
        'name_zh': '教育网',
        'abb_upper': 'CE',
    },
    'OT': {
        'name_zh': '其它',
        'abb_upper': 'OT',
    }
}

ispmap = {
  '258': {'cn': '电信', 'en': 'ct'},
  '259': {'cn': '移动', 'en': 'cm'},
  '260': {'cn': '教育网', 'en': 'ce'},
  '262': {'cn': '铁通', 'en': 'ctt'},
  '263': {'cn': '华数', 'en': 'wasu'},
  '264': {'cn': '联通', 'en': 'un'},
  # '265': {'cn': '其它', 'en': 'ot'},
  '265': {'cn': '其它', 'en': 'other'},
  '269': {'cn': '鹏博士', 'en': 'pbs'},
  '307': {'cn': '方正', 'en': 'fd'},
  '308': {'cn': '广电', 'en': 'oc'},
  '318': {'cn': 'BGP', 'en': 'bgp'}
}

def get_isp(val, cate='id', isp_list=None):
    try:
        if isp_list:
            isp = None
            if cate == 'id':
                isp = [i for i in isp_list if i['noc_id'] == int(val)]
            elif cate == 'name':
                isp = [i for i in isp_list if i['name'].upper() == val]
            if isp:
                return isp[0]
        return {}
    except:
        return {}




if __name__ == '__main__':
    # a = {k.lower(): v['name_zh'] for k, v in isp.items()}
    from pprint import pprint
    # pprint(a)

    for k, v in city.items():
        v['abb_upper'] = v['abb'].upper()
    pprint(city)