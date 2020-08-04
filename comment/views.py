from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.contrib.contenttypes.models import ContentType
from .settings import Rest
from .serializers import CommentSerializer
from .models import CommentModel


class CommentView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def post(self, request, *args, **kwargs):
        rest = Rest()
        try:
            obj_model = request.data.get('model', '')
            content_type_obj = ContentType.objects.filter(model=obj_model).first()
            request.data['content_type'] = content_type_obj.id
            ser_obj = CommentSerializer(data=request.data)
            if ser_obj.is_valid():
                ser_obj.save()
                rest.set(30100, '评论成功')
            else:
                rest.set(30101, '评论失败,参数校验失败', ser_obj.errors)
        except Exception as e:
            rest.set(30199, str(e))

        return Response(rest.__dict__)

    def get(self, request, *args, **kwargs):
        rest = Rest()
        try:
            # 获取视频的所有评论信息, 并返回
            obj_id = int(request.query_params.get('id', -1))
            if obj_id == -1:
                rest.set(30001, '获取评论失败,参数缺失,id未传')
                return Response(rest.__dict__)
            obj_model = request.query_params.get('model', '')
            if not obj_model:
                rest.set(30002, '获取评论失败,参数缺失, models未传')
                return Response(rest.__dict__)
            content_type_obj = ContentType.objects.filter(model=obj_model).first()
            if not content_type_obj:
                rest.set(30003, '获取评论失败,参数错误,model错误')
                return Response(rest.__dict__)
            queryset = CommentModel.objects.filter(content_type_id=content_type_obj.id, object_id=obj_id).all()
            if not queryset:
                rest.set(30004, '暂无评论')
                return Response(rest.__dict__)
            ser_obj = CommentSerializer(queryset, many=True)
            rest.set(30000, '获取评论信息成功', ser_obj.data)

        except Exception as e:
            rest.set(30099, str(e))

        return Response(rest.__dict__)

    def delete(self, request, *args, **kwargs):
        rest = Rest()
        try:
            user_id = request.data.get('user', ''),
            time = request.data.get('time', '')
            if CommentModel.objects.filter(user_id=user_id, time=time).exists():
                CommentModel.objects.filter(user_id=user_id, time=time).delete()
                rest.set(30200, '评论删除成功')
            else:
                rest.set(30201, '评论不存在')
        except Exception as e:
            rest.set(30299, str(e))
        return Response(rest.__dict__)