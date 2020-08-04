from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from ..serializers import *
from ..settings import Rest
from utils.paginator import MyPagination


class VideoView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, *args, **kwargs):
        rest = Rest()
        try:
            category = request.query_params.get('category')

            if category:
                queryset = DancingVideo.objects.filter(category__title=category).order_by('-posted_time')
            else:
                queryset = DancingVideo.objects.order_by('-posted_time')
            paginator = MyPagination()
            total = paginator.get_count(queryset)
            page_list = paginator.paginate_queryset(queryset, request)
            ser_obj = VideoSerializer(page_list, many=True)
            if queryset:
                rest.set(20000, 'VideoView获取舞蹈视频信息,成功', ser_obj.data)
                rest.total = total
            else:
                rest.set(20001, 'VideoView获取舞蹈视频信息,没有更多视频了')
                rest.total = 0

        except ValueError as e:
            rest.set(20002, str(e))

        except Exception as e:
            rest.set(20099, str(e))
        return Response(rest.__dict__)


class CategoryView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, *args, **kwargs):
        rest = Rest()

        try:
            count = int(request.query_params.get('count', 0))
            queryset = Category.objects.order_by('weight')

            if count != 0:
                queryset = queryset[:count]

            ser_obj = CategorySerializer(queryset, many=True)
            rest.set(20100, 'CategoryView获取舞蹈种类信息,成功', ser_obj.data)

        except ValueError as e:
            rest.set(20101, str(e))

        except Exception as e:
            rest.set(20199, str(e))

        return Response(rest.__dict__)
