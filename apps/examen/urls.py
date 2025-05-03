from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.examen.views import (
    CategoriaViewSet, CursoViewSet, ExamenViewSet,
    PreguntaViewSet, AlternativaViewSet, NotaViewSet
)

router = DefaultRouter()
router.register(r'categorias', CategoriaViewSet)
router.register(r'cursos', CursoViewSet)
router.register(r'examenes', ExamenViewSet)
router.register(r'preguntas', PreguntaViewSet)
router.register(r'alternativas', AlternativaViewSet)
router.register(r'notas', NotaViewSet)

urlpatterns = [
    path('', include(router.urls)),
]