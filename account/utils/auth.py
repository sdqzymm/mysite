import time
from django.core.cache import cache
from rest_framework.authentication import TokenAuthentication, get_authorization_header
from rest_framework.exceptions import AuthenticationFailed
from ..models import UserProfileModel
from ..settings import Rest, AUTH_TYPE


class MyAuth(TokenAuthentication):
    keyword = 'Token'
    is_my_user = True
    app_key = None
    open_id = None
    redirect_url = None
    rest = Rest()

    def authenticate(self, request):
        # 10201-10219, 跳转登录页面 10299: 服务器错误,报警 跳转登录
        # 10221表示账号被冻结, 前台提示用户后跳转解封或登录页面
        # 10231表示本站用户access_token过期,前台跳转刷新token
        # 10232表示三方平台账号使用超过24小时,前台跳转重新登录
        # 请求头中-> Authorization: Token 401f7ac837da42b97f613d789819ff93537bee6a  取到Token xxx
        try:
            auth = get_authorization_header(request).split()
            if not auth:
                self.rest.set(10201, '请求头未携带token令牌')
                raise AuthenticationFailed

            if len(auth) != 2 or auth[0].lower() != self.keyword.lower().encode():
                self.rest.set(10202, '无效的token令牌，请求头携带token格式不正确')
                raise AuthenticationFailed

            try:
                token = auth[1].decode()
            except UnicodeError:
                self.rest.set(10203, '无效的token值，token中含有无效的字符')
                raise AuthenticationFailed

            auth_type = int(request.data.get('auth_type', '') or -1)
            self.app_key = request.data.get('app_key', '')
            self.open_id = request.data.get('open_id', '')
            self.redirect_url = request.get_full_path()
            print(self.redirect_url)

            if auth_type not in AUTH_TYPE or auth_type == 9:
                self.rest.set(10204, '参数错误, auth_type有误')
                raise AuthenticationFailed
            if auth_type not in [0, 1, 2]:  # 判定是否本站注册用户
                self.is_my_user = False

            return self.authenticate_credentials(token)

        except Exception as e:
            if type(e) == AuthenticationFailed:
                raise AuthenticationFailed(self.rest.__dict__)
            self.rest.set(10299, '未知错误')
            raise AuthenticationFailed(self.rest.__dict__)

    def authenticate_credentials(self, key):
        # 从缓存中查找
        if self.is_my_user:
            # 属于本站用户的请求
            if not self.app_key:
                self.rest.set(10205, '参数错误,未提供app_key')
                raise AuthenticationFailed
            user_obj = UserProfileModel.objects.filter(app_key=self.app_key).first()
            if not user_obj:
                self.rest.set(10206, '参数错误,app_key错误')
                raise AuthenticationFailed
            if not user_obj.is_active:
                self.rest.set(10221, '用户被冻结')
                raise AuthenticationFailed
            # 校验token
            self.check_token(key, self.rest)
        else:
            # 三方平台账号的请求
            if not self.open_id:
                self.rest.set(10207, '参数错误,未提供open_id')
                raise AuthenticationFailed
            self.check_token(key, self.rest)
            user_obj = '三方平台用户'
        return user_obj, key

    def check_token(self, key, rest):
        token = cache.get(self.app_key if self.is_my_user else self.open_id)
        if not token:
            rest.set(10208, 'token不存在')
            raise AuthenticationFailed
        if key != token.get('access_token', ''):
            rest.set(10209, 'token不匹配')
            raise AuthenticationFailed
        elif token.get('access_expire', 0) < time.time():
            if self.is_my_user:
                rest.set(10231, '本站用户token超时,请刷新token')
                rest.data['redirect_url'] = self.redirect_url
            else:
                rest.set(10232, '三方平台账号token超时,请重新登录')
            raise AuthenticationFailed



