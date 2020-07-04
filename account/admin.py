from django.contrib import admin
from .models import *
from django.utils import timezone


@admin.register(UserProfileModel)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'mobile', 'nickname', 'type', 'gender', 'last_login')

    # def last_login_time_(self, obj):
    #
    #     return timezone.datetime.fromtimestamp(int(obj.last_login_time))
    # last_login_time_.short_description = '上次登录时间'


@admin.register(UserAuthModel)
class UserAuthAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'type', 'identity', 'password')


@admin.register(UserDetailModel)
class UserDetailAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'name', 'mobile', 'birthday', 'address',)

    def mobile(self, obj):
        return obj.user.mobile

    mobile.short_description = '手机'
