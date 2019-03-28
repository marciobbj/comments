from apps.v1_core.views import CommentAPIView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('comment', CommentAPIView, base_name='comment')

urlpatterns = router.urls
