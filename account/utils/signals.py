from uuid import uuid4
from django.dispatch import Signal
from django.utils import timezone
from .redis_cache import set_user_token, set_others_token
logged_in = Signal(providing_args=['auth_type', 'key'])


def auto_login(auth_type, key, sender=None):
    access_token = uuid4()
    refresh_token = uuid4()
    if auth_type in [1, 2, 3]:
        set_user_token(access_token, refresh_token, key)
    else:
        set_others_token(access_token, key)
    if sender:
        sender.last_login = timezone.now()
        return access_token, refresh_token


logged_in.connect(auto_login)