from uuid import uuid4
from django.core.mail import send_mail
from django.core.cache import cache
from ..settings import EMAIL_ACTIVE_HTML, EMAIL_HOST_USER


def send_active_email(user, email):
    app_key = user.app_key
    token = str(uuid4())
    cache.set(f'{app_key}_active', token, timeout=60 * 5)
    html_message = EMAIL_ACTIVE_HTML % (user.nickname, token, app_key, email)
    send_mail(
        '邮箱激活', '', EMAIL_HOST_USER, [email], fail_silently=False,
        html_message=html_message
    )
