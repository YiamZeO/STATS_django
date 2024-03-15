from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from pets.services import PetsService


class PetsViewSet(viewsets.ViewSet):
    @action(methods=['GET'], detail=False)
    def pets_categories(self, request):
        return Response(PetsService().pets_categories().to_dict())

    @action(methods=['GET'], detail=False)
    def visitors_data(self, request):
        return Response(PetsService().visitors_data(request.GET.get('date_from'), request.GET.get('date_to')).to_dict())
