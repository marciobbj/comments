from apps.v1_core.views import CommentAPIView
from apps.v1_core.views import ReplyAPIView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('comment', CommentAPIView, base_name='comment')
router.register('reply', ReplyAPIView, base_name='reply')

urlpatterns = router.urls
