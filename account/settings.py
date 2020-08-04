# 注: 使用本account应用的功能, 需要在项目settings中配置如下:
# app中加载本应用
# AUTH_USER_MODEL: 指定用户类为本应用下的UserProfileModel
# MEDIA相关: MEDIA_ROOT MEDIA_URL
# 项目url配置media路由: from django.views.static import serve  re_path(r'^media/(?P<path>.*)$', serve, {'document_root': MEDIA_ROOT}),
# Rest: 自定义消息返回-> code; msg; data; set方法
# 邮箱配置:  协议,端口,账号,授权码等

from mysite.settings.settings import MEDIA_ROOT, MEDIA_URL, Rest, EMAIL_HOST_USER

# 本站用户注册需要提供手机号,密码,并且通过手机短信验证码校验
AUTH_TYPE = {  # 备注了不同类型的权限
    0: '手机号',  # 登录,请求
    1: '用户名',  # 登录,请求, 绑定
    2: '邮箱',    # 登录,请求, 绑定
    3: '微信',    # 登录,请求, 绑定
    4: 'QQ',      # 登录,请求, 绑定
    5: '微博',    # 登录,请求, 绑定
    9: '短信验证码',  # 注册
}

EMAIL_ACTIVE_HTML = '<h1>%s, 欢迎您注册本站</h1> \
                  请点击下面的链接激活您的邮箱账号<br/> \
                  <a href="http://127.0.0.1:8000/api/account/active/?token=%s&app_key=%s&email=%s"> \
                  http://127.0.0.1:8000/api/account/active/</a>'



