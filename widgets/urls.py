from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import DegWidgetViewSet, test

router = DefaultRouter()
router.register(r'deg_widgets', DegWidgetViewSet, basename='deg_widgets')

urlpatterns = [
    path('', include(router.urls)),
    path('test/', test, name='test')
]
