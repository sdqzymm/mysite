from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from .models import UserProfileModel, UserDetailModel, UserAuthModel
from mysite.settings import MEDIA_URL
from hashlib import md5


class UserProfileSerializer(serializers.ModelSerializer):
    type_ = serializers.CharField(source='get_type_display', read_only=True)
    gender_ = serializers.CharField(source='get_gender_display', read_only=True)
    avatar_ = serializers.SerializerMethodField(read_only=True)

    def get_avatar_(self, obj):
        if obj.avatar:
            return MEDIA_URL + str(obj.avatar)
        return ''

    def create(self, validated_data):
        validated_data['nickname'] = validated_data.get('nickname') or f'{validated_data.get("mobile")[:3]}******{validated_data.get("mobile")[-2:]}'
        validated_data['password'] = make_password(validated_data.get('password'))
        validated_data['app_key'] = md5(validated_data['mobile'].encode('utf8')).hexdigest()
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data['password'] = instance.set_password(validated_data.get('password'))
        return super().update(instance, validated_data)

    def validate(self, attrs):

        return attrs

    class Meta:
        model = UserProfileModel
        # fields = '__all__'
        exclude = ['groups', 'user_permissions', 'is_superuser',]
        extra_kwargs = {
            'password': {
                'error_messages': {
                    'required': '密码不能为空',
                    'blank': '密码不能为空',
                }
            },
            'mobile': {
                'error_messages': {
                    'blank': '手机号不能为空',
                    'required': '手机号不能为空'
                }
            },
            'created_time': {'read_only': True},
            'login_time': {'read_only': True},
            'type': {'write_only': True},
            'gender': {'write_only': True},
            'avatar': {'write_only': True},
            'is_staff': {'write_only': True, 'default': False},
            'is_active': {'default': True},
            'app_key': {'read_only': True}
        }
