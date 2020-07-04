from django.db import transaction
from django.contrib.auth.hashers import make_password
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import UserProfileSerializer
from .models import UserAuthModel
from .utils.signals import logged_in
from mysite.settings import Rest
from .settings import AUTH_TYPE
from utils.exceptions import RollBackException


class RegView(APIView):
    def post(self, request):
        rest = Rest()
        try:
            # TODO: 首先短信验证码校验
            # 创建用户
            ser_obj = UserProfileSerializer(data=request.data)

            if not ser_obj.is_valid():
                rest.set(10001, '注册失败,数据校验错误', ser_obj.errors)
                return Response(rest.__dict__)
            user_obj = ser_obj.save()

            auth_type = int(request.data.get('auth_type', -1))
            if auth_type not in AUTH_TYPE:
                rest.set(10002, '注册失败,注册类型不存在')
                return Response(rest.__dict__)

            elif auth_type != 9:
                # 三方平台账号绑定注册
                open_id = request.data.get('open_id')
                try:
                    with transaction.atomic():
                        user_auth_obj, created = UserAuthModel.objects.get_or_create(type=auth_type, identity=open_id)
                        if not created:
                            # 该平台账号已经注册,
                            raise RollBackException
                        # 三方平台账号与用户绑定
                        user_auth_obj.user_id = user_obj.pk
                except RollBackException:
                    rest.set(10010, '用户注册成功,但绑定三方平台账号失败,该平台账号已经在本站注册')
                    return Response(rest.__dict__)

            # 自动登录, 缓存token, 修改登录时间
            access_token, refresh_token = logged_in.send(sender=user_obj, auth_type=auth_type, key=user_obj.app_key)

            rest.set(10000, '注册成功', ser_obj.data)
            rest.data['access_token'] = access_token
            rest.data['refresh_token'] = refresh_token

        except Exception:
            rest.set(10099, '未知错误')

        return Response(rest.__dict__)


class LoginView(APIView):
    def post(self, request):
        rest = Rest()
        try:
            auth_type = int(request.data.get('auth_type', -1))
            if auth_type not in AUTH_TYPE:
                rest.set(10101, '参数错误,type未提供或有误')
                return Response(rest.__dict__)

            if auth_type not in [0, 1, 2]:
                # 三方平台账号登录
                open_id = request.data.get('open_id', '')
                if not open_id:
                    rest.set(10102, '参数错误,三方账号登录未携带open_id')
                    return Response(rest.__dict__)
                logged_in.send(sender='', auth_type=auth_type, key=open_id)

                rest.set(10110, '登陆成功')
                return Response(rest.__dict__)

            # 本站注册用户登录
            rest, user_obj = self.user_auth(request, auth_type, rest)
            access_token, refresh_token = logged_in.send(sender=user_obj, auth_type=auth_type, key=user_obj.app_key)
            rest.data['access_token'] = access_token
            rest.data['refresh_token'] = refresh_token

        except Exception:
            rest.set(10199, '未知错误')

        return Response(rest.__dict__)

    def user_auth(self, request, auth_type, rest):
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
            user_auth_obj = UserAuthModel.objects.filter(type=0, mobile=mobile).first()
            if user_auth_obj is None:
                rest.set(10104, '参数错误,手机号不存在')
                return rest, None
        elif auth_type == 1:
            # 用户名密码登录
            if not username:
                rest.set(10105, '参数错误,未携带用户名')
                return rest, None
            user_auth_obj = UserAuthModel.objects.filter(type=1, username=username).first()
            if user_auth_obj is None:
                rest.set(10106, '参数错误,用户名错误')
                return rest, None
        elif auth_type == 2:
            # 邮箱密码登录
            if not email:
                rest.set(10107, '参数错误,未携带邮箱')
                return rest, None
            user_auth_obj = UserAuthModel.objects.filter(type=0, email=email).first()
            if user_auth_obj is None:
                rest.set(10108, '参数错误,邮箱不存在')
                return rest, None
        if not user_auth_obj.password == make_password(password):
            rest.set(10108, '参数错误,密码错误')
            return rest, None
        if not user_auth_obj.user_id:
            rest.set(10108, '参数错误,密码错误')
            return rest, None
        user_obj = user_auth_obj.user
        rest.set(10100, '登陆成功', UserProfileSerializer(instance=user_obj).data)
        return rest, user_obj


class RefreshTokenView(APIView):
    def post(self, request):
        pass
