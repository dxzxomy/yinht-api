from . import spec
from flask_restful import Api
from .api import BaseNavAPI, NavListAPI, NavTreeList, UploadAvatarAPI

spec_api = Api(spec)


spec_api.add_resource(NavListAPI, 'nav', endpoint='navs')
spec_api.add_resource(BaseNavAPI, 'nav/<int:nav_id>', endpoint='nav')
spec_api.add_resource(NavTreeList, 'nav_tree', endpoint='nav_tree')
spec_api.add_resource(UploadAvatarAPI, 'upload_avatar', endpoint='upload_avatar')