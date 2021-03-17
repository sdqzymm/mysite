from django.db.models import F
from django.core.cache import cache
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from ..settings import Rest
from ..models import DancingVideo


class PlayView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, *args, **kwargs):
        rest = Rest()

        try:
            video_id = request.query_params.get('id')
            key = f'play_{video_id}'
            # 当前阅读数
            initial = 0
            if cache.get(key) is None:
                initial = DancingVideo.objects.filter(pk=video_id).first().play_num
            else:
                initial = cache.get(key)
            # 阅读数+1, 写入redis
            current = initial + 1
            cache.set(key, current, timeout=3600 * 24 * 7)
            # 阅读数每增加100(根据流量),更新mysql中的值(另外可以开一个定时任务, 每天凌晨4点将redis中的所有阅读数更新到mysql)
            if current%100 == 0:
                DancingVideo.objects.filter(pk=video_id).update(play_num=current)
            rest.set(20200, '阅读数加1', {
                'play_num': current
            })
        except Exception as e:
            rest.set(20299, str(e))

        return Response(rest.__dict__)