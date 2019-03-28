from apps.v1_core.models import Comment
from apps.v1_core.models import Reply
from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class CommentSerializer(serializers.ModelSerializer):
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = (
            'content', 'replies', 'user',
            'likes_comments', 'created_at',
        )

    def get_replies(self, instance):
        return Reply.objects.filter(comment=instance.id).values('content')


class ReplySerializer(serializers.ModelSerializer):
    class Meta:
        model = Reply
        fields = ('content', 'comment', 'likes_replies', 'created_at',)
