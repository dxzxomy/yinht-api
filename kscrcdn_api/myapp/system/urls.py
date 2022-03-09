from . import system
from flask_restful import Api
from .api import UserLogoutAPI, UserLoginAPI, UserInfoAPI
from .api.user import BaseUserAPI, UserListAPI
from .api.user import UserRoleRelAPI

system_api = Api(system)
system_api.add_resource(UserLoginAPI, 'auth/user/login', endpoint='login')
system_api.add_resource(UserLogoutAPI, 'auth/user/logout', endpoint='logout')
system_api.add_resource(UserInfoAPI, 'system/user/info', endpoint='userinfo')
system_api.add_resource(UserListAPI, 'system/user', endpoint='users')
system_api.add_resource(BaseUserAPI, 'system/user/<int:user_id>', endpoint='user')
