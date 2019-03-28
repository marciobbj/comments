from apps.v1_core.views import CommentAPIView
from apps.v1_core.views import LikeCommentAPIView
from apps.v1_core.views import LikeReplyAPIView
from apps.v1_core.views import ReplyAPIView
from django.urls import include
from django.urls import path
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('comment', CommentAPIView, base_name='comment')
router.register('reply', ReplyAPIView, base_name='reply')

urlpatterns = [
    path('', include(router.urls)),
    path(
        'comment/<int:comment_id>/like/',
        LikeCommentAPIView.as_view(), name='like_comment',
    ),
    path(
        'reply/<int:reply_id>/like/',
        LikeReplyAPIView.as_view(), name='like_reply',
    ),
]
