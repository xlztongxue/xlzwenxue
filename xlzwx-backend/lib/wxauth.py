import requests
import datetime
from . import redis_utils
import uuid
import ujson as json
import redis_lock
from .WXBizDataCrypt import WXBizDataCrypt
from flask import current_app

WXAPP_ID = 'wxdab2c9193cb7e2a9'

WXAPP_SECRET = '66ebd51238192cb95dfc82c4cdff034f'


def get_wxapp_session_key(code):
    url = 'https://api.weixin.qq.com/sns/jscode2session?appid=%s&secret=%s&js_code=%s&grant_type=authorization_code' % (
    WXAPP_ID, WXAPP_SECRET, code)
    data = requests.get(url).json()
    print(data)
    return data


def get_user_info(encryptedData, iv, session_key):
    pc = WXBizDataCrypt(WXAPP_ID, session_key)
    return pc.decrypt(encryptedData, iv)


def get_access_token():
    cache_key = 'access_token'
    with redis_lock.Lock(current_app.redis, cache_key, expire=10, auto_renewal=True):
        return _get_access_token(cache_key)


def _get_access_token(cache_key):
    token = current_app.redis.get(cache_key)
    if not token:
        url = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=%s&secret=%s' % \
              (WXAPP_ID, WXAPP_SECRET)
        token = requests.get(url).text
        assert 'access_token' in token
        current_app.redis.set(cache_key, token, ex=7000)
    return json.loads(token)['access_token']


def get_wxacode(scene):
    cache_key = 'cache:wxacode:' + scene
    wxacode = current_app.redis.get(cache_key)
    if wxacode:
        return wxacode
    url = 'https://api.weixin.qq.com/wxa/getwxacodeunlimit?access_token=' + get_access_token()
    resp = requests.post(url, json={'scene': scene})
    if not resp.content:
        return ''
    current_app.redis.set(cache_key, resp.content, ex=604800)
    return resp.content
