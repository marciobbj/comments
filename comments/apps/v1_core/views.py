from django.contrib.auth import get_user_model
from django.shortcuts import render

# Create your views here.
from rest_framework import mixins, viewsets, status
from rest_framework.response import Response
from rest_framework.utils import json

from apps.v1_core.models import Comment
from apps.v1_core.serializers import CommentSerializer

User = get_user_model()

class CommentAPIView(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    lookup_url_kwarg = 'instance_id'
    serializer_class = CommentSerializer
    queryset = Comment.objects.all()

    def get_object(self):
        return Comment.objects.get(pk=self.kwargs['instance_id'])

    def update(self, request, *args, **kwargs):
        comment_id = self.kwargs.get('instance_id', None)
        if comment_id is None:
            return Response(data={'response': 'instance id not found'}, status=status.HTTP_400_BAD_REQUEST)
        instance = Comment.objects.get(pk=comment_id)
        instance.content = self.request.data['content']
        instance.save()
        return Response(data={'response': 'updated'}, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_200_OK)
