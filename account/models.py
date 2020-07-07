from functools import wraps
from hashlib import md5
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager, AbstractBaseUser, User, PermissionsMixin
from django.core import validators
from django.utils.deconstruct import deconstructible


# 手机号校验器
@deconstructible
class UnicodeMobileValidator(validators.RegexValidator):
    regex = r'^((13[0-9])|(14[05679])|(15[0-35-9])|(16[67])|(17[235-8])|(18[0-9])|(19[189]))\d{8}$'
    message = '请输入正确的11位手机号'


# 用户名校验器
@deconstructible
class UnicodeUsernameValidator(validators.RegexValidator):
    regex = r'^(?!\d|_)(?!\d+$)(?![a-zA-Z]+$)(?!_+$)[a-zA-Z0-9_]{6,30}$'
    message = '6-30个字符，必须使用字母、数字和下划线的组合，不能以数字或下划线开头'


# 密码校验器
@deconstructible
class UnicodePasswordValidator(validators.RegexValidator):
    regex = r'^(?!_)(?!_+$)[a-zA-Z0-9_]{6,}$'
    message = '至少6个字符，可以使用字母、数字或下划线，不能以下划线开头，不能全部是下划线'


# 给用户表save方法自定义装饰器, save后自从生成手机号密码认证表并绑定用户
def decorate_save(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        res = func(self, *args, **kwargs)
        # 绑定UserAuth
        if not UserAuthModel.objects.filter(identity=self.mobile).exists():
            UserAuthModel.objects.get_or_create(user_id=self.pk, identity=self.mobile, password=self.password)
        return res
    return wrapper


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, password, **extra_fields):
        user = self.model(**extra_fields)
        user.nickname = user.nickname or f'{user.mobile[:3]}******{user.mobile[-2:]}'
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_user(self, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('app_key', md5(extra_fields.get('mobile').encode('utf8')).hexdigest())

        return self._create_user(password, **extra_fields)

    def create_superuser(self, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('type', 0)
        extra_fields.setdefault('app_key', md5(extra_fields.get('mobile').encode('utf8')).hexdigest())

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(password, **extra_fields)


def upload_avatar(instance, filename):
    return f'avatar/{instance.nickname}-{filename}'


class UserProfileModel(AbstractBaseUser, PermissionsMixin):
    mobile_validator = UnicodeMobileValidator()
    password_validator = UnicodePasswordValidator()

    mobile = models.CharField(
        '手机号', max_length=11, unique=True, validators=[mobile_validator],
        error_messages={'unique': '该手机号已经注册'},
        help_text='11位手机号',
    )
    password = models.CharField(
        '密码', error_messages={'max_length': '密码最多128位'}, max_length=128, blank=True, null=True,
        validators=[password_validator], help_text='本站用户登录使用的密码,三方平台账号登录时无需使用密码'
    )
    app_key = models.CharField('用户身份key', max_length=64, unique=True, blank=True, help_text='本站用户注册后拥有,唯一身份标识')
    nickname = models.CharField('昵称', max_length=30, default='', help_text='昵称')
    type_choices = ((0, '管理员'), (1, '普通用户'), (2, 'vip用户'),)
    type = models.IntegerField('用户类型', choices=type_choices, default=1)
    gender_choices = ((0, '女'), (1, '男'))
    gender = models.IntegerField('性别', choices=gender_choices, default=0, help_text='性别')
    avatar = models.ImageField('头像', upload_to=upload_avatar, blank=True, null=True, help_text='头像')
    getui_client_id = models.CharField('个推客户端ID', max_length=128, null=True, blank=True)
    is_staff = models.BooleanField('是否职工', default=False,
                                   help_text='决定用户能否登录admin管理后台,默认不能')
    is_active = models.BooleanField('是否激活', default=True,
                                    help_text='默认激活,当要删除用户时,可以改成False')
    created_time = models.DateTimeField('注册时间', auto_now_add=True)

    @decorate_save
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def clean(self):
        super().clean()

    def __str__(self):
        return f'<用户: {self.nickname}>'

    __repr__ = __str__

    objects = UserManager()
    USERNAME_FIELD = 'mobile'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = '用户'
        verbose_name_plural = verbose_name
        swappable = 'AUTH_USER_MODEL'


class UserAuthModel(models.Model):
    user = models.ForeignKey(to='UserProfileModel', verbose_name='用户', on_delete=models.CASCADE,
                             related_name='auths', help_text='关联用户')
    # 注册时使用手机短信验证码, 登录时不提供短信验证码接口(省钱)
    auth_choices = ((0, '手机号密码'), (1, '用户名密码'), (2, '邮箱密码'), (3, '微信'), (4, 'QQ'), (5, '微博'))
    type = models.IntegerField('认证类型', choices=auth_choices, help_text='用户认证类型', default=0)
    identity = models.CharField(
        '认证标识', max_length=128, unique=True,
        help_text='用户登录的标识,如手机号密码登录,则存储手机号,三方平台登录,则存储open_id'
    )
    is_valid = models.BooleanField('是否激活', blank=True, null=True, help_text='绑定邮箱时需要激活')
    password = models.CharField(
        '密码', error_messages={'max_length': '密码最多128位'}, max_length=128, blank=True, null=True,
        help_text='本站用户登录使用的密码,三方平台账号登录时无需使用密码'
    )

    def __str__(self):
        return f'<用户认证信息: {self.user}--{self.get_type_display()}>'

    __repr__ = __str__

    class Meta:
        verbose_name = '用户认证表'
        verbose_name_plural = verbose_name


# 用户详情表
class UserDetailModel(models.Model):
    user = models.OneToOneField(to='UserProfileModel', on_delete=models.CASCADE, verbose_name='用户',
                                help_text='连接用户表', related_name='detail')
    name = models.CharField('姓名', max_length=16, null=True, blank=True, help_text='姓名')
    signature = models.CharField('个性签名', max_length=128, help_text='个性签名', null=True, blank=True)
    birthday = models.CharField('生日', max_length=16, help_text='生日', null=True, blank=True)
    remark = models.TextField('备注', help_text='备注', null=True, blank=True)
    address = models.CharField('家庭住址', max_length=32, help_text='家庭住址', null=True, blank=True)

    def __str__(self):
        return f'<用户详情: {self.user}>'

    __repr__ = __str__

    class Meta():
        verbose_name = '用户详情表'
        verbose_name_plural = verbose_name
