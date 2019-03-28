from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.v1_core.models import Comment

User = get_user_model()

class CommentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields = ('content', 'user',)

