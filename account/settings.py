AUTH_TYPE = [
    0,  # 手机号密码登录,
    1,  # 用户名密码登录
    2,  # 邮箱密码登录
    3,  # 微信账号登录,注册
    4,  # QQ账号登录,注册
    5,  # 微博账号登录,注册
    9,  # 手机短信验证码注册
]


class Rest:
    def __init__(self):
        self.code = 0
        self.msg = ''
        self.data = None

    def set(self, code=0, msg='', data=None):
        self.code = code
        self.msg = msg
        self.data = data