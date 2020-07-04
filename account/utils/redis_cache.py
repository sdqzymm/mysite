import time
from django.core.cache import cache


def set_user_token(access_token, refresh_token, app_key):
    token = {
        'access_token': access_token,
        'access_expire': int(time.time()) + 7200,
        'refresh_token': refresh_token,
        'refresh_expire': int(time.time()) + 3600*24*15
    }
    cache.set(app_key, token, timeout=None)


def set_others_token(access_token, open_id):
    token = {
        'access_token': access_token,
        'access_expire': int(time.time()) + 3600 * 24,  # 每24小时要重新登录
    }
    cache.set(open_id, token, timeout=3600*24*7)
