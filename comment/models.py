from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from account.models import UserProfileModel


class CommentModel(models.Model):
    content = models.TextField('评论内容', help_text='评论内容')
    p_comment = models.ForeignKey(to='self', verbose_name='父评论', on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey(to=UserProfileModel, verbose_name='评论用户', on_delete=models.CASCADE,
                             help_text='评论用户', related_name='posted_comments')
    to = models.ForeignKey(to=UserProfileModel, verbose_name='回复用户', on_delete=models.DO_NOTHING, null=True, blank=True,
                           help_text='有父评论的情况下表示为回复评论,存在回复的用户对象', related_name='received_comments')
    time = models.CharField('评论的时间戳', max_length=13, help_text='评论的时间,以时间戳表示')
    # 以下表示该评论属于哪个对象, 比如视频的评论, 商品的评论等等
    content_type = models.ForeignKey(to=ContentType, verbose_name='对应的表', on_delete=models.CASCADE, help_text='对应的模型类')
    object_id = models.IntegerField('主键id', help_text='在对应表中具体对象的id')
    content_object = GenericForeignKey('content_type', 'object_id')
