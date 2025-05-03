from rest_framework.routers import DefaultRouter
from apps.biblioteca.views import LibroViewSet

router = DefaultRouter()
router.register(r'libros', LibroViewSet, basename='libro')

urlpatterns = router.urls