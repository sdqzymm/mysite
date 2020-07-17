from rest_framework.views import APIView
from rest_framework.response import Response
from ..serializers import *
from ..settings import Rest, PAGE_SIZE


class VideoView(APIView):
    authentication_classes = []

    def get(self, request, *args, **kwargs):
        version = request.version
        rest = Rest()
        if version == 'v1':
            try:
                page = int(request.query_params.get('page', 0))
                size = int(request.query_params.get('size', PAGE_SIZE))
                category = request.query_params.get('category')

                if category:
                    queryset = DancingVideo.objects.filter(category__title=category).order_by('-posted_time')[
                           page * size:(page+1) * size
                           ]
                else:
                    queryset = DancingVideo.objects.order_by('-posted_time')[
                               page * size:(page + 1) * size
                               ]
                ser_obj = VideoSerializer(queryset, many=True)
                if queryset:
                    rest.code = 2000
                    rest.msg = 'VideoView获取舞蹈视频信息,成功'
                    rest.data = ser_obj.data
                else:
                    rest.code = 2001
                    rest.msg = 'VideoView获取舞蹈视频信息,没有更多视频了'

            except ValueError as e:
                rest.code = 2002
                rest.msg = 'VideoView获取舞蹈视频信息,参数错误'
                rest.data = str(e)

            except Exception as e:
                rest.code = 2003
                rest.msg = 'VideoView获取舞蹈视频信息,未预知错误'
                rest.data = str(e)

        return Response(rest.__dict__)


class CategoryView(APIView):
    authentication_classes = []

    def get(self, request, *args, **kwargs):
        rest = Rest()

        try:
            count = int(request.query_params.get('count', 0))
            queryset = Category.objects.order_by('weight')

            if count != 0:
                queryset = queryset[:count]

            ser_obj = CategorySerializer(queryset, many=True)
            rest.code = 2010
            rest.msg = 'CategoryView获取舞蹈种类信息,成功'
            rest.data = ser_obj.data

        except ValueError as e:
            rest.code = 2011
            rest.msg = 'CategoryView获取舞蹈种类信息,参数错误'
            rest.data = str(e)

        except Exception as e:
            rest.code = 2012
            rest.msg = 'CategoryView获取舞蹈种类信息,未预知错误'
            rest.data = str(e)

        return Response(rest.__dict__)
