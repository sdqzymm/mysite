import os
from aliyunsdkcore.client import AcsClient

from aliyunsdkcore.request import CommonRequest

client = AcsClient(os.environ['ACCESS_KEY'], os.environ['ACCESS_KEY_SECRET'], 'cn-hangzhou')


class MobileCaptchaRequest(CommonRequest):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_accept_format('json')
        self.set_domain('dysmsapi.aliyuncs.com')
        self.set_method('POST')
        self.set_protocol_type('https')  # https | http
        self.set_version('2017-05-25')
        self.add_query_param('RegionId', "cn-hangzhou")
        self.add_query_param('SignName', "小乔舞蹈")
        self.add_query_param('TemplateCode', "SMS_196146395")


def send_mobile_captcha(mobile, code):
    request = MobileCaptchaRequest()
    request.set_action_name('SendSms')
    request.add_query_param('PhoneNumbers', mobile)
    request.add_query_param('TemplateParam', {'code': code})
    response = client.do_action_with_exception(request)

    print(f'{mobile}获取了验证码')

    return str(response, encoding='utf-8')
