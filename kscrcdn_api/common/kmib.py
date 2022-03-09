import asyncio
import aiosnmp
import ipaddress


interface = {
    'ifindex': '1.3.6.1.2.1.2.2.1.1',
    'ifdescr': '1.3.6.1.2.1.2.2.1.2',
    'iftype': '1.3.6.1.2.1.2.2.1.2',
    'ifhighspeed': '1.3.6.1.2.1.31.1.1.1.15',
    'ifadminstatus': '1.3.6.1.2.1.2.2.1.7',
    'ifoperstatus': '1.3.6.1.2.1.2.2.1.8',
    'iflastchange': '1.3.6.1.2.1.2.2.1.9',
    'ifinerrors': '1.3.6.1.2.1.2.2.1.14',
    'ifouterrors': '1.3.6.1.2.1.2.2.1.20',
    'ifname': '1.3.6.1.2.1.31.1.1.1.1',
    'ifalias': '1.3.6.1.2.1.31.1.1.1.18',
    'ifphysaddress': '1.3.6.1.2.1.2.2.1.6'
}

interface_l3 = {
    'ipadentaddr': '1.3.6.1.2.1.4.20.1.1',
    'ipadentifindex': '1.3.6.1.2.1.4.20.1.2',
    'ipadentnetmask': '1.3.6.1.2.1.4.20.1.3',
}

mac = {
    # mac地址
    'macaddress': '1.3.6.1.2.1.17.4.3.1.1',
    'macport': '1.3.6.1.2.1.17.4.3.1.2',
}

macportifindex = '1.3.6.1.2.1.17.1.4.1.2'


route = {
    # route的不兼容, 并发处理会有数据对不上, 但是单独获取数据对得上
    # 'iproutedest': '1.3.6.1.2.1.4.21.1.1',
    # 'iproutemask': '1.3.6.1.2.1.4.21.1.11',
    # 'iproutenexthop': '1.3.6.1.2.1.4.21.1.7',
    # 'ifindex': '1.3.6.1.2.1.4.21.1.2',
    'ipcidrroutedest': '1.3.6.1.2.1.4.24.4.1.1',
    'ipcidrroutemask': '1.3.6.1.2.1.4.24.4.1.2',
    'ipcidrroutenexthop': '1.3.6.1.2.1.4.24.4.1.4',
    'ifindex': '1.3.6.1.2.1.4.24.4.1.5',
}

arp = {
    'ifindex': '1.3.6.1.2.1.4.22.1.1',
    'arpmacaddress': '1.3.6.1.2.1.4.22.1.2',
    'arpipaddress': '1.3.6.1.2.1.4.22.1.3',
}

lldp = {
    'lldpremportid': '1.0.8802.1.1.2.1.4.1.1.7',
    'lldpremportdesc': '1.0.8802.1.1.2.1.4.1.1.8',
    'lldpremsysname': '1.0.8802.1.1.2.1.4.1.1.9',
    'lldpremsysdesc': '1.0.8802.1.1.2.1.4.1.1.10',
    # 'lldplocportid': '1.0.8802.1.1.2.1.3.7.1.3',
    # 'lldplocportdesc': '1.0.8802.1.1.2.1.3.7.1.4'
}

entity = {
    'class': '1.3.6.1.2.1.47.1.1.1.1.5',
    'softwarerev': '1.3.6.1.2.1.47.1.1.1.1.10',
    'sn': '1.3.6.1.2.1.47.1.1.1.1.11'
}
