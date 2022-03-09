from flask import Blueprint

spec = Blueprint(
    'spec',
    __name__,
    template_folder='templates',
    static_folder='static'
)

from . import views
from . import urls
