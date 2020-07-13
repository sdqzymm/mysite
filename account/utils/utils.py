import random
import string
from django.core.cache import cache


def get_mobile_captcha():
    return ''.join(random.sample(string.digits, 6))


def check_mobile_captcha(request, rest):
    captcha = request.data.get('captcha', '')
    mobile = request.data.get('mobile', '')
    captcha_cache = cache.get(mobile)
    if not captcha_cache:
        rest.set(10007, '验证码失效')
        return rest
    if captcha + mobile != cache.get(mobile):
        rest.set(10006, '验证码错误')
        return rest
