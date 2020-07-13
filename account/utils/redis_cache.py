import time
from django.core.cache import cache


def set_user_token(access_token, refresh_token, app_key):
    token = {
        'access_token': access_token,
        'access_expire': int(time.time()) + 7200,
        'refresh_token': refresh_token,
        'refresh_expire': int(time.time()) + 3600*24*15
    }
    try:
        cache.set(app_key, token, timeout=None)
    except Exception as e:
        print(str(e), type(e), 'set_user_token')
        cache.set(app_key, token, timeout=None)


def set_others_token(access_token, open_id):
    token = {
        'access_token': access_token,
        'access_expire': int(time.time()) + 3600 * 24,  # 三方平台账号每24小时要重新登录, 前
    }
    try:
        cache.set(open_id, token, timeout=3600*25)  # 25小时后直接清除缓存
    except Exception as e:
        print(str(e), type(e), 'set_others_token')
        cache.set(open_id, token, timeout=3600 * 25)


def set_refresh_token(access_token, refresh_token, app_key):
    """
    保存旧的token, 客户端并发请求可能拿着旧的refresh_token来刷新
    10s内生成同一个token,避免客户端并发请求获取到不同的刷新token值
    """
    if not cache.get(f'{app_key}_old'):
        old_token = cache.get(app_key)
        cache.set(f'{app_key}_old', old_token, timeout=30)
    token = cache.get(f'{app_key}_refresh')
    if not token:
        token = {
            'access_token': access_token,
            'access_expire': int(time.time()) + 7200,
            'refresh_token': refresh_token,
            'refresh_expire': int(time.time()) + 3600 * 24 * 15
        }
        cache.set(f'{app_key}_refresh', token, timeout=10)
    else:
        access_token = token.get('access_token')
        refresh_token = token.get('refresh_token')
    cache.set(app_key, token, timeout=None)
    return access_token, refresh_token


