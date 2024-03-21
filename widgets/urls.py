from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import DegWidgetViewSet, DegWidgetFormViewSet

router = DefaultRouter()
router.register(r'deg_widgets', DegWidgetViewSet, basename='deg_widgets')
router.register(r'deg_widgets_f', DegWidgetFormViewSet, basename='deg_widgets_f')

urlpatterns = [
    path('', include(router.urls))
]
