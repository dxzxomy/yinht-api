# -*- coding:utf-8 -*-

from flask import Blueprint

system = Blueprint(
    'system',
    __name__,
    template_folder='templates',
    static_folder='static'
)

from . import views
from . import urls
