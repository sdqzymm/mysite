from django.urls import re_path
from .views import *

urlpatterns = [
    re_path(r'comment/$', CommentView.as_view()),
]