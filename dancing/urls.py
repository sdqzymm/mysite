from django.urls import path, re_path
from .views.collect_view import *

urlpatterns = [
    # 采集视频信息,存储到数据库(因为没有大容量服务器或者资源提供商,视频图片等暂时只存储资源地址,这里可能涉及占用别人的资源提供商带宽)
    re_path('collect/video/$', CollectVideo.as_view(), name='collect_video'),
    re_path('collect/tag/$', CollectTag.as_view(), name='collect_tag'),
]