from django.db import models
from account.models import UserProfileModel


class Category(models.Model):
    """
    舞蹈的分类, 暂时分为: 中国舞 芭蕾舞 现代舞 爵士舞 时尚舞 拉丁舞 摩登舞 踢踏舞 抖音 肚皮舞 儿童舞 教学 其他
    """
    title = models.CharField('类别', max_length=32, unique=True, help_text='具体的分类,如舞蹈下的中国舞,芭蕾舞等等')
    type_choice = [
        (0, '舞蹈'), (1, '文学'), (2, '科学'), (3, '绘画'), (4, '歌唱')
    ]
    type = models.IntegerField('类型', choices=type_choice, help_text='大的分类,如舞蹈,绘画,歌唱', default=0)
    weight = models.IntegerField('权重', default=1)

    class Meta:
        verbose_name = '分类表'
        verbose_name_plural = verbose_name
        db_table = verbose_name

    def __repr__(self):
        return self.title

    __str__ = __repr__


class DancingTag(models.Model):
    title = models.CharField('标签分类', max_length=32, unique=True)

    class Meta:
        verbose_name = '标签分类表'
        verbose_name_plural = verbose_name
        db_table = verbose_name

    def __repr__(self):
        return self.title

    __str__ = __repr__


class DancingVideo(models.Model):
    name = models.CharField('舞蹈名', max_length=128)
    title = models.CharField('视频标题', max_length=128)
    cover = models.CharField('视频封面', null=True, blank=True, max_length=256)
    mp4 = models.CharField('mp4地址', max_length=256)
    m3u8 = models.CharField('m3u8地址', max_length=256)
    brief = models.TextField('简介', null=True, blank=True, max_length=1024)
    category = models.ForeignKey('Category', verbose_name='舞蹈分类', on_delete=models.CASCADE, null=True, blank=True)
    tags = models.ManyToManyField('DancingTag', verbose_name='标签')
    # 其他网站扒的视频的作者信息
    author_name = models.CharField('作者', null=True, blank=True, max_length=64)
    author_avatar = models.CharField('作者头像地址', max_length=256,)
    # 本网站用户上传的视频的作者信息
    user = models.ForeignKey(UserProfileModel, null=True, blank=True, on_delete=models.CASCADE, verbose_name='上传用户')
    posted_time = models.DateTimeField('发表时间', null=True, blank=True)
    posted_by = models.CharField('转载自', default='中舞网', max_length=32)
    play_num = models.IntegerField('播放次数', default=0)
    # 后续可以添加: 播放数 点赞数 评论-> 评论表 这些高频字段可以做redis缓存

    class Meta:
        verbose_name = '视频表'
        verbose_name_plural = verbose_name
        db_table = verbose_name
        unique_together = ('title', 'author_name')

    def __repr__(self):
        return self.title

    __str__ = __repr__