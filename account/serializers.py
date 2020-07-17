from hashlib import md5
from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from .models import UserProfileModel, UserDetailModel
from .settings import MEDIA_URL


class UserProfileSerializer(serializers.ModelSerializer):
    # type_ = serializers.CharField(source='get_type_display', read_only=True)
    # gender_ = serializers.CharField(source='get_gender_display', read_only=True)
    avatar_ = serializers.SerializerMethodField(read_only=True)
    mobile_ = serializers.SerializerMethodField(read_only=True)
    photoList = serializers.SerializerMethodField(read_only=True)
    name = serializers.CharField(source='detail.name', read_only=True)
    signature = serializers.CharField(source='detail.signature', read_only=True)
    birthday = serializers.CharField(source='detail.birthday', read_only=True)

    def get_avatar_(self, obj):
        avatar = obj.avatar
        if avatar:
            return MEDIA_URL + str(avatar)
        return ''

    def get_mobile_(self, obj):
        mobile = obj.mobile
        return f'{mobile[0:3]}******{mobile[-2:]}'

    def get_photoList(self, obj):
        return [{'image': MEDIA_URL + str(photo)} for photo in obj.photos.order_by('index')]

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
                'write_only': True,
                'error_messages': {
                    'blank': '手机号不能为空',
                    'required': '手机号不能为空'
                }
            },
            'created_time': {'read_only': True},
            'last_login': {'read_only': True},
            # 'type': {'write_only': True},
            # 'gender': {'write_only': True},
            'avatar': {'write_only': True},
            'is_staff': {'write_only': True, 'default': False},
            'is_active': {'default': True},
            'app_key': {'read_only': True}
        }


# 仅用来更改用户属性
class EditProfileSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='detail.name', write_only=True, allow_blank=True)
    signature = serializers.CharField(source='detail.signature', write_only=True, allow_blank=True)
    birthday = serializers.CharField(source='detail.birthday', write_only=True, allow_blank=True)

    def update(self, instance, validated_data):
        UserDetailModel.objects.filter(user=instance).update(**validated_data['detail'])
        del validated_data['detail']
        return super().update(instance, validated_data)

    class Meta:
        model = UserProfileModel
        fields = ['nickname', 'gender', 'name', 'signature', 'birthday', 'avatar']


