from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from utils.cython_utils.test_service import Test
from pets.services import PetsService


class PetsViewSet(viewsets.ViewSet):

    @action(methods=['GET'], detail=False)
    @swagger_auto_schema(
        operation_description='Возврат всех категорий'
    )
    def pets_categories(self, request):
        return Response(PetsService().pets_categories().to_dict())

    @action(methods=['GET'], detail=False)
    @swagger_auto_schema(
        operation_description='Извлечение данных для графика "Посетители"',
        manual_parameters=[
            openapi.Parameter('date_from', openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description='Дата начала промежутка'),
            openapi.Parameter('date_to', openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description='Дата конца промежутка'),
        ],
    )
    def visitors_data(self, request):
        return Response(PetsService().visitors_data(request.GET.get('date_from'), request.GET.get('date_to')).to_dict())

    @action(methods=['GET'], detail=False)
    @swagger_auto_schema(
        operation_description='Извлечение данных для графика "Переходы и действия"',
        manual_parameters=[
            openapi.Parameter('date_from', openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description='Дата начала промежутка'),
            openapi.Parameter('date_to', openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description='Дата конца промежутка'),
            openapi.Parameter('category', openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description='Категория'),
        ],
    )
    def get_transitions_and_actions_data(self, request):
        if request.GET.get('category'):
            res = PetsService().get_transitions_and_actions_data(request.GET.get('date_from'),
                  request.GET.get('date_to'), request.GET.get('category')).to_dict()
            res['cython_c++_vector_test'] = Test().generate_and_sort_numbers(15)
            return Response(res)
        else:
            pets_service = PetsService()
            res = [pets_service.get_transitions_and_actions_data(request.GET.get('date_from'),
                  request.GET.get('date_to'), category).to_dict() for category in pets_service.pets_categories().data]
            for r in res:
                r['meta']['cython_c++_vector_test'] = Test().generate_and_sort_numbers(15)
            return Response(res)
