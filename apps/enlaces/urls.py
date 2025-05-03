from rest_framework.routers import DefaultRouter
from apps.enlaces.views import EnlaceClaseGrabadaViewSet, EnlaceCursoViewSet

router = DefaultRouter()
router.register(r'clases', EnlaceClaseGrabadaViewSet, basename='clases')
router.register(r'cursos', EnlaceCursoViewSet, basename='cursos')

urlpatterns = router.urls