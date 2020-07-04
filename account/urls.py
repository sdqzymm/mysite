from django.urls import re_path
from .views import *


urlpatterns = [
    re_path('^reg/$', RegView.as_view(), name='reg'),
    re_path('^login/$', LoginView.as_view(), name='login'),
    re_path('^refresh/$', RefreshTokenView.as_view(), name='refresh_token'),
]