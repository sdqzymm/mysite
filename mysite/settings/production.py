from .settings import *

DEBUG = False

ALLOWED_HOSTS = ['*']

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'mysite',
        'HOST': os.environ["TENCENT_YUN_IP"],
        'POST': 3306,
        'USER': 'sdqzymm',
        'PASSWORD': os.environ['PASSWORD'],
    }
}

# 静态文件收集
STATIC_ROOT = '/data/nginx/mysite/static'

EMAIL_PORT = 25  # 邮件端口,阿里云要改465(25端口很难打开)
EMAIL_USE_TLS = True  # TLS和SSL

# 日志文件
ADMINS = (
    ('admin', os.environ['EMAIL_HOST_USER']),
)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'mysite.log',
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
        }
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': False,
        }
    },
}
