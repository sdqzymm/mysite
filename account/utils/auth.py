import time
from rest_framework.authentication import TokenAuthentication, get_authorization_header
from rest_framework.exceptions import AuthenticationFailed
from account.models import UserProfileModel
from mysite.settings import Rest
from django.core.cache import cache
from account.settings import AUTH_TYPE


class MyAuth(TokenAuthentication):
    keyword = 'Token'
    is_my_user = True
    app_key = None
    open_id = None

    def authenticate(self, request):
        # 10201-10219, 跳转登录页面 10299: 服务器错误,报警 跳转登录
        # 10221表示账号被冻结, 前台提示用户后跳转解封或登录页面
        # 10231表示access_token过期,前台跳转刷新token
        # 10232表示三方平台账号使用超过24小时,前台跳转重新登录
        rest = Rest()
        # 请求头中-> Authorization: Token 401f7ac837da42b97f613d789819ff93537bee6a  取到Token xxx
        try:
            auth = get_authorization_header(request).split()

            if not auth:
                rest.set(10201, '请求头未携带token令牌')
                raise AuthenticationFailed(rest.__dict__)

            if len(auth) != 2 or auth[0].lower() != self.keyword.lower().encode():
                rest.set(10202, '无效的token令牌，请求头携带token格式不正确')
                raise AuthenticationFailed(rest.__dict__)

            try:
                token = auth[1].decode()
            except UnicodeError:
                rest.set(10203, '无效的token值，token中含有无效的字符')
                raise AuthenticationFailed(rest.__dict__)

            auth_type = int(request.data.get('auth_type', -1))
            self.app_key = request.data.get('app_key', '')

            if auth_type not in AUTH_TYPE:
                rest.set(10204, '参数错误, auth_type有误')
                raise AuthenticationFailed(rest.__dict__)
            if auth_type not in [0, 1, 2]:  # 判定是否本站注册用户
                self.is_my_user = False

            return self.authenticate_credentials(token)
        except Exception:
            rest.set(10299, '未知错误')
            raise AuthenticationFailed(rest.__dict__)

    def authenticate_credentials(self, key):
        rest = Rest()
        # 从缓存中查找
        if self.is_my_user:
            # 属于本站用户的请求
            user_obj = UserProfileModel.objects.filter(app_key=self.app_key).first()
            if not user_obj:
                rest.set(10205, '参数错误,app_key不存在')
                raise AuthenticationFailed(rest.__dict__)
            if not user_obj.is_active:
                rest.set(10221, '用户被冻结')
                raise AuthenticationFailed(rest.__dict__)
            # 校验token
            self.check_token(key, rest)
        else:
            # 三方平台账号的请求
            self.check_token(key, rest)
            user_obj = '三方平台用户'
        return user_obj, key

    def check_token(self, key, rest):
        token = cache.get(self.app_key or self.open_id)
        if not token:
            rest.set(10206, 'token不存在')
            raise AuthenticationFailed(rest.__dict__)
        if key != token.get('access_token', ''):
            rest.set(10207, 'token不匹配')
            raise AuthenticationFailed(rest.__dict__)
        elif token.get('access_expire', 0) < time.time():
            rest.set(10231, 'token超时,请刷新token')
            if self.open_id:
                rest.set(10232, '三方平台账号token超时,请重新登录')
            raise AuthenticationFailed(rest.__dict__)



