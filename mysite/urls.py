"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path, include
from django.views.static import serve
from .settings.settings import MEDIA_ROOT

urlpatterns = [
    path('admin/', admin.site.urls),

    # 账号相关路由配置
    re_path('^api/account/((?P<version>[v1|2]+)/)?', include(('account.urls', 'account'), namespace='account')),

    # 舞蹈相关路由配置
    re_path('^api/dancing/((?P<version>[v1|2]+)/)?', include(('dancing.urls', 'dancing'), namespace='dancing')),

    # 评论下你管路由配置
    re_path('^api/comment/((?P<version>[v1|2]+)/)?', include(('comment.urls', 'comment'), namespace='comment')),

    # media路径配置
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': MEDIA_ROOT}),
]
