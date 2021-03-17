import time
from django.utils import timezone
from django.core.cache import cache
from rest_framework import serializers
from .models import *


class VideoSerializer(serializers.ModelSerializer):
    # 自定义部分字段作为正序
    category_info = serializers.SerializerMethodField(read_only=True)
    user_info = serializers.SerializerMethodField(read_only=True)
    tags_info = serializers.SerializerMethodField(read_only=True)
    datetime = serializers.SerializerMethodField(read_only=True)
    timestamp = serializers.SerializerMethodField(read_only=True)
    play_num = serializers.SerializerMethodField(read_only=True)

    def get_category_info(self, obj):
        category_obj = obj.category
        return {
            'id': category_obj.id,
            'title': category_obj.title
        }

    def get_user_info(self, obj):
        user_obj = obj.user
        if user_obj is None:
            return '非本站用户上传'
        return {
            'id': user_obj.id,
            'username': str(user_obj)
        }

    def get_tags_info(self, obj):
        tags_queryset = obj.tags.all()
        return [{
            'id': tag.id,
            'title': tag.title
        } for tag in tags_queryset]

    def get_datetime(self, obj):
        t = obj.posted_time + timezone.timedelta(hours=8)
        t = str(t).split('.')[0]
        return t

    def get_timestamp(self, obj):
        t = obj.posted_time + timezone.timedelta(hours=8)
        t = time.mktime(t.timetuple())
        return t

    def get_play_num(self, obj):
        # 先从缓存中读取
        key = f'play_{obj.id}'
        play_num = cache.get(key)
        # 缓存未命中,读取数据库
        if not play_num:
            play_num = DancingVideo.objects.filter(pk=obj.id).first().play_num
        return play_num

    class Meta:
        model = DancingVideo
        exclude = []
        # 将已经自定义的字段设置为只写(即反序) 添加校验器
        extra_kwargs = {
            'category': {'write_only': True},
            'user': {'write_only': True},
            'posted_time': {'write_only': True},
            'tags': {'write_only': True, 'validators': []},
        }

    # 定义局部钩子  校验单个字段
    def validate_title(self, value):
        # value就是title字段的值
        if value == '去死吧':
            raise serializers.ValidationError('标题不能这样写')
        return value

    # 定义全局钩子  可以在此校验所有字段
    def validate(self, attrs):
        # attrs: 字典,包含了所有传过来的字段
        if not attrs.get('title'):
            attrs['title'] = '无题'
            return attrs


class CategorySerializer(serializers.ModelSerializer):
    type_show = serializers.SerializerMethodField(read_only=True)

    def get_type_show(self, obj):
        return obj.get_type_display()

    class Meta:
        model = Category
        fields = '__all__'
        extra_kwargs = {
            'type': {'write_only': True}
        }