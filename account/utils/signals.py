from uuid import uuid4
from django.dispatch import Signal
from django.utils import timezone
from .redis_cache import set_user_token, set_others_token, set_refresh_token

logged_in = Signal(providing_args=['auth_type', 'key'])
token_refreshed = Signal(providing_args=['key'])


def auto_login(sender, auth_type, key, **kwargs):
    # 登录成功, 本站注册用户缓存token, 刷新登录时间, 并且返回用户信息 三方账号仅缓存token
    access_token = str(uuid4())
    refresh_token = str(uuid4())
    if auth_type in [0, 1, 2, 9]:
        set_user_token(access_token, refresh_token, key)
    else:
        set_others_token(access_token, key)
    if sender:
        sender.last_login = timezone.now()
        sender.save()
        return access_token, refresh_token


def refresh(sender, key, **kwargs):
    access_token = str(uuid4())
    refresh_token = str(uuid4())
    access_token, refresh_token = set_refresh_token(access_token, refresh_token, key)
    sender.last_login = timezone.now()
    return access_token, refresh_token


logged_in.connect(auto_login)
token_refreshed.connect(refresh)