from rest_framework.routers import DefaultRouter
from apps.horarios.views import HorarioViewSet

router = DefaultRouter()
router.register(r'', HorarioViewSet, basename='horario')

urlpatterns = router.urls