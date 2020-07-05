import time
from django.db import transaction
from django.core.cache import cache
from django.contrib.auth.hashers import check_password, make_password
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import UserProfileSerializer
from .models import UserAuthModel, UserProfileModel
from .utils.signals import logged_in, token_refreshed
from .settings import Rest
from .settings import AUTH_TYPE
from .utils.exceptions import RollBackException, OldRefreshTokenException


class RegView(APIView):
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        rest = Rest()
        try:
            # TODO: 首先短信验证码校验
            auth_type = int(request.data.get('auth_type') or -1)
            if auth_type not in AUTH_TYPE:
                rest.set(10002, '注册失败,注册类型不存在')
                return Response(rest.__dict__)
            if auth_type in [0, 1, 2]:
                rest.set(1003, '注册失败,本站暂不支持仅用密码注册')
                return Response(rest.__dict__)
            # 创建用户
            ser_obj = UserProfileSerializer(data=request.data)
            if not ser_obj.is_valid():
                rest.set(10001, '注册失败,数据校验错误', ser_obj.errors)
                return Response(rest.__dict__)
            # 事务操作, 先创建用户, 如果是三方平台要绑定用户,绑定失败进行回滚
            try:
                with transaction.atomic():
                    user_obj = ser_obj.save()
                    if auth_type != 9:
                        # 三方平台账号绑定注册
                        open_id = request.data.get('open_id', '')
                        if not open_id:
                            rest.set(10004, '三方平台账号未提供open_id, 无法绑定, 用户注册失败')
                            raise RollBackException
                        user_auth_obj, created = UserAuthModel.objects.get_or_create(type=auth_type, identity=open_id)
                        if not created:
                            # 该平台账号已经注册,
                            rest.set(10005, '三方平台账号已在本站绑定, 无法再次绑定, 用户注册失败')
                            raise RollBackException
                        # 三方平台账号与用户绑定
                        user_auth_obj.user_id = user_obj.pk
            except RollBackException:
                return Response(rest.__dict__)

            # 自动登录, 缓存token, 修改登录时间
            access_token, refresh_token = logged_in.send(sender=user_obj, auth_type=auth_type, key=user_obj.app_key)[0][1]
            rest.set(10000, '注册成功', ser_obj.data)
            rest.data['access_token'] = access_token
            rest.data['refresh_token'] = refresh_token

        except Exception as e:
            rest.set(10099, str(e))

        return Response(rest.__dict__)


class LoginView(APIView):
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        rest = Rest()
        try:
            auth_type = int(request.data.get('auth_type') or -1)
            if auth_type not in AUTH_TYPE:
                rest.set(10101, '参数错误,type未提供或有误')
                return Response(rest.__dict__)

            if auth_type not in [0, 1, 2]:
                # 三方平台账号登录
                open_id = request.data.get('open_id', '')
                if not open_id:
                    rest.set(10102, '参数错误,三方账号登录未携带open_id')
                    return Response(rest.__dict__)
                # 三方用户登录成功, 缓存token
                logged_in.send(sender='', auth_type=auth_type, key=open_id)

                rest.set(10110, '登陆成功')
                return Response(rest.__dict__)

            # 本站注册用户登录
            rest, user_obj = self.user_auth(request, auth_type, rest)
            if user_obj is None:
                return Response(rest.__dict__)

            # 本站用户登录成功, 缓存token, 返回用户信息
            access_token, refresh_token = logged_in.send(sender=user_obj, auth_type=auth_type, key=user_obj.app_key)[0][1]
            rest.set(10100, '登陆成功', UserProfileSerializer(instance=user_obj).data)
            rest.data['access_token'] = access_token
            rest.data['refresh_token'] = refresh_token

        except Exception as e:
            rest.set(10199, str(e))

        return Response(rest.__dict__)

    def user_auth(self, request, auth_type, rest):
        # 本站注册用户登录
        password = request.data.get('password', '')
        username = request.data.get('username', '')
        mobile = request.data.get('mobile', '')
        email = request.data.get('email', '')
        user_auth_obj = None

        if auth_type == 0:
            # 手机号密码登录
            if not mobile:
                rest.set(10103, '参数错误,未携带手机号')
                return rest, None
            user_auth_obj = UserAuthModel.objects.filter(type=0, identity=mobile).first()
            if user_auth_obj is None:
                rest.set(10104, '参数错误,手机号不存在')
                return rest, None
        elif auth_type == 1:
            # 用户名密码登录
            if not username:
                rest.set(10105, '参数错误,未携带用户名')
                return rest, None
            user_auth_obj = UserAuthModel.objects.filter(type=1, identity=username).first()
            if user_auth_obj is None:
                rest.set(10106, '参数错误,用户名不存在')
                return rest, None
        elif auth_type == 2:
            # 邮箱密码登录
            if not email:
                rest.set(10107, '参数错误,未携带邮箱')
                return rest, None
            user_auth_obj = UserAuthModel.objects.filter(type=0, identity=email).first()
            if user_auth_obj is None:
                rest.set(10108, '参数错误,邮箱不存在')
                return rest, None

        # 校验用户
        user_obj = user_auth_obj.user
        if not user_obj:
            rest.set(10112, '用户不存在')
            return rest, None
        if not user_obj.is_active:
            rest.set(10113, '用户被冻结')
            return rest, None
        # 校验密码:
        if not user_obj.check_password(password):
            rest.set(10111, '参数错误,密码错误')
            return rest, None
        return rest, user_obj


class RefreshTokenView(APIView):
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        rest = Rest()
        try:
            app_key = request.data.get('app_key', '')
            refresh_token = request.data.get('refresh_token', '')

            if not (app_key and refresh_token):
                rest.set(10401, '参数错误, 未携带app_key或refresh_token')
                return Response(rest.__dict__)

            user_obj = UserProfileModel.objects.filter(app_key=app_key).first()
            if not user_obj:
                rest.set(10402, '参数错误, app_key用户不存在')
                return Response(rest.__dict__)

            token = cache.get(app_key)
            old_token = cache.get(f'{app_key}_old')

            if not token:
                rest.set(10403, '用户token不存在')
                return Response(rest.__dict__)

            try:
                if refresh_token != token.get('refresh_token'):
                    if refresh_token == old_token.get('refresh_token'):
                        raise OldRefreshTokenException
                    rest.set(10404, '参数错误, refresh_token有误')
                    return Response(rest.__dict__)
                expire = token.get('refresh_expire', 0)
                if expire <= time.time():
                    rest.set(10405, 'refresh_token已过期, 请重新登录')
                    return Response(rest.__dict__)
            except OldRefreshTokenException:
                pass

            # 刷新token
            access_token, refresh_token = token_refreshed.send(sender=user_obj, key=app_key)[0][1]
            redirect_url = request.data.get('redirect_url')
            rest.set(10400, '已刷新token,请跳转url')
            rest.data['redirect_url'] = request.data.get('redirect_url')
            if not redirect_url:
                rest.set(10400, '已刷新token,跳转首页')
            rest.data['access_token'] = access_token
            rest.data['refresh_token'] = refresh_token

        except Exception as e:
            rest.set(10499, str(e))

        return Response(rest.__dict__)


class TestView(APIView):
    def post(self, request, *args, **kwargs):
        pass