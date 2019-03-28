from rest_framework.routers import DefaultRouter

from apps.v1_core.views import CommentAPIView

router = DefaultRouter()
router.register('comment', CommentAPIView, base_name='comment')

urlpatterns = router.urls
