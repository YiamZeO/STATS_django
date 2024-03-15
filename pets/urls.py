from rest_framework.routers import DefaultRouter
from django.urls import path, include
from pets.views import PetsViewSet

router = DefaultRouter()
router.register(r'pets', PetsViewSet, basename='pets')
urlpatterns = [
    path('', include(router.urls))
]
