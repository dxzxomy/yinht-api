import logging
import traceback
import os
import json
import requests
import gzip
import base64
import hashlib
from urllib import parse
from flask import request
from flask_restful import Resource


log = logging.getLogger()


class UserInfoAPI(Resource):

    def get(self):
        info = {
            'roles': ['admin'],
            'introduction': 'I am a super administrator',
            'avatar': 'https://wpimg.wallstcn.com/f778738c-e4f8-4870-b634-56703b4acafe.gif',
            'name': 'Super Admin'
        }
        return dict(code=20200, data=info, msg='Success')


class UserLoginAPI(Resource):

    def post(self):
        print(request.json)
        info = {
            'roles': ['admin'],
            'introduction': 'I am a super administrator',
            'avatar': 'https://wpimg.wallstcn.com/f778738c-e4f8-4870-b634-56703b4acafe.gif',
            'name': 'Super Admin'
        }
        return dict(code=20200, data=info, msg='Success')


class UserLogoutAPI(Resource):

    def post(self):
        return dict(code=20000, data='success')

