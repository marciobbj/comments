from apps.v1_core.models import Comment
from apps.v1_core.serializers import CommentSerializer
from django.contrib.auth import get_user_model
from rest_framework import filters
from rest_framework import mixins
from rest_framework import status
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
# Create your views here.

User = get_user_model()


class CommentAPIView(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    lookup_url_kwarg = 'instance_id'
    serializer_class = CommentSerializer
    permission_classes = IsAuthenticated,
    filter_backends = (filters.SearchFilter, filters.OrderingFilter,)
    search_fields = ('user__username',)
    ordering_fields = ('username', 'created_at',)

    def get_object(self):
        return Comment.objects.get(pk=self.kwargs['instance_id'])

    def get_queryset(self):
        ordering_by = self.request.query_params.get('ordering', None)
        if ordering_by is not None:
            try:
                return Comment.objects.all().order_by(f'{ordering_by}')
            except Exception as e:
                raise e
        return Comment.objects.all()

    def update(self, request, *args, **kwargs):
        comment_id = self.kwargs.get('instance_id', None)
        if comment_id is None:
            return Response(
                data={'response': 'instance id not found'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        instance = Comment.objects.get(pk=comment_id)
        instance.content = self.request.data['content']
        instance.save()
        return Response(
            data={'response': 'updated'},
            status=status.HTTP_200_OK,
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_200_OK)
