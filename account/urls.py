from django.urls import re_path
from .views import *


urlpatterns = [
    re_path('^reg/$', RegView.as_view(), name='reg'),
    re_path('^login/$', LoginView.as_view(), name='login'),
    re_path('^refresh_token/$', RefreshTokenView.as_view(), name='refresh_token'),
    re_path('^test/$', TestView.as_view(), name='test_view'),
    re_path('^blind/$', BlindView.as_view(), name='blind'),
    re_path('^active/$', ActiveView.as_view(), name='active'),
    re_path('^captcha/$', CaptchaView.as_view(), name='captcha'),
    re_path('^profile/$', ProfileView.as_view(), name='profile'),

]
