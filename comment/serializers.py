from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from .models import CommentModel


class CommentSerializer(ModelSerializer):
    pid = serializers.SerializerMethodField(read_only=True)
    userId = serializers.IntegerField(source='user_id', read_only=True)
    avatar = serializers.ImageField(source='user.avatar', read_only=True)
    gender = serializers.IntegerField(source='user.gender', read_only=True)
    nickname = serializers.CharField(source='user.nickname', read_only=True)
    toUserId = serializers.IntegerField(source='to_id', read_only=True)
    toUser = serializers.CharField(source='to.nickname', read_only=True)
    toGender = serializers.IntegerField(source='to.gender', read_only=True)

    def get_pid(self, obj):
        return obj.p_comment_id or -1

    class Meta:
        model = CommentModel
        exclude = []
        extra_kwargs = {
            'p_comment': {'write_only': True},
            'user': {'write_only': True},
            'to': {'write_only': True},
            'object_id': {'write_only': True},
            'content_type': {'write_only': True},
        }