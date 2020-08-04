from django.views import View
from django.shortcuts import HttpResponse
from django.http import JsonResponse
from ..utils.collect import collect_video, collect_tag
from ..models import DancingVideo, DancingTag, Category
from django.db import transaction


class CollectVideo(View):
    def get(self, request, *args, **kwargs):
        size = request.GET.get('size')
        video_list = collect_video(size)
        # # 批量插入
        # obj_list = [DancingVideo(**video) for video in video_list
        #             if not DancingVideo.objects.filter(title=video['title']).exists()]
        # try:
        #     with transaction.atomic():
        #         DancingVideo.objects.bulk_create(obj_list)
        # except Exception as e:
        #     return HttpResponse(e)
        """如果不存在则插入数据, 并且添加tag多对多字段和category外键字段"""
        err_list = []
        for video in video_list:
            try:
                with transaction.atomic():
                    tag_list = video.pop('tags')
                    tags = [DancingTag.objects.get_or_create(title=i)[0] for i in tag_list]
                    category_id = get_category(tag_list)
                    video_obj, flag = DancingVideo.objects.get_or_create(**video, category_id=category_id)
                    if flag:
                        video_obj.tags.set(tags)
            except Exception as e:
                err_list.append(str(e))
                continue
        if err_list:
            return JsonResponse(err_list, safe=False)
        return HttpResponse('OK')


class CollectTag(View):
    def get(self, request, *args, **kwargs):
        tag_list = collect_tag()
        obj_list = [DancingTag(**tag) for tag in tag_list
                    if not DancingTag.objects.filter(title=tag.get('title')).exists()]
        try:
            # bulk_create()自带事务操作
            DancingTag.objects.bulk_create(obj_list)
        except Exception as e:
            return HttpResponse(e)
        return HttpResponse('OK')


def get_category(tags):
    # 根据tags自动选择一个category给舞蹈视频(tags去匹配以下列表)
    category_list = ['中国', '芭蕾', '现代', '时尚', '爵士', '拉丁', '街舞',
                     '摩登', '抖音', '热舞', '踢踏', '民族', '民间', '古典',
                     '肚皮舞', '伦巴', '桑巴', '恰恰', '斗牛', '牛仔',
                     '华尔兹', 'hiphop', '少儿', '儿童', '流行', '学习',
                     '练习', '教学', '基础', '技巧', '知识', 'popping',
                     '维也纳', '探戈', '快步', '狐步', '迪斯科', '锐舞']
    category = ''
    for item in category_list:
        for tag in tags:
            if item in tag:
                category = item
                break
        if category:
            break
    if category in ['民族', '民间', '古典']:
        category = '中国'
    elif category in ['伦巴', '桑巴', '恰恰', '斗牛', '牛仔']:
        category = '拉丁'
    elif category in ['华尔兹', '维也纳', '探戈', '快步', '狐步']:
        category = '摩登'
    elif category in ['迪斯科', '锐舞', '街舞', '热舞', 'hiphop', 'popping', '流行']:
        category = '时尚'
    elif category in ['少儿']:
        category = '儿童'
    elif category in ['练习', '教学', '基础', '技巧', '知识', '学习']:
        category = '教学'
    elif not category:
        category = '其他'
    category_id = Category.objects.filter(title__contains=category).first().id
    return category_id
