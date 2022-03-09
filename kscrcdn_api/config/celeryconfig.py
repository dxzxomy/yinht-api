# -*- coding:utf-8 -*-

from kombu import Exchange, Queue

broker_url = 'redis://:kscredispassword@redis-server:6379/0'
result_backend = 'redis://:kscredispassword@redis-server:6379/1'
timezone = 'Asia/Shanghai'
accept_content = ['json']
task_serializer = 'json'
result_serializer = 'json'
worker_max_tasks_per_child = 5   # 每个worker child最多处理任务数后就销毁
worker_concurrency = 10   # 默认为cpu核心数量,IO操作频繁可酌情调大
task_soft_time_limit = 60 * 30   # 单任务最大执行时间, in seconds
# task_soft_time_limit = 3   # 单任务最大执行时间, in seconds

task_default_queue = 'default'
task_default_exchange_type = 'direct'
task_default_routing_key = 'default'

worker_hijack_root_logger = False   # 禁用celery日志,使用自定义logger
worker_max_memory_per_child = 12000  # 12M
result_expires = 60 * 60 * 24 * 90   # 任务数据保留时间

imports = [
    'kscrcdn_api.mycelery.tasks.switch.sniff_sw',
    'kscrcdn_api.mycelery.tasks.switch.dispatch_sw',
    'kscrcdn_api.mycelery.tasks.install.pxe',
    'kscrcdn_api.mycelery.tasks.install.init',
]

task_queues = (
    Queue('default', Exchange('default'), routing_key='default'),
    Queue('swtask', Exchange('swtask'), routing_key='swtask'),
    Queue('swtasks', Exchange('swtasks'), routing_key='swtasks'),
)

# task_routes = ([
#     ('kscrcdn_api.mycelery.tasks.test.test_task.*', {'queue': 'test_queue', 'routing_key': 'test_queue'}),
# ])

# Demo setting
# task_queues = {
#     'cpubound': {
#         'exchange': 'cpubound',
#         'routing_key': 'cpubound',
#     },
# }

# task_routes = {
#     'tasks.add': {
#         'queue': 'cpubound',
#         'routing_key': 'tasks.add',
#         'serializer': 'json',
#     },
# }

try:
    from .local_celeryconfig import *
except:
    pass
