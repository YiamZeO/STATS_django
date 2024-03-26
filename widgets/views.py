import datetime
import io
import json
from urllib.parse import quote

from django.http import HttpResponse
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action, parser_classes
from rest_framework.parsers import MultiPartParser, JSONParser
from rest_framework.response import Response

from widgets.models import DegWidget, DegTypes
from widgets.serializers import DegWidgetSerializer
from widgets.services import DegDataService


class DegWidgetFormViewSet(viewsets.ViewSet):
    """
    ViewSet для запросов с form параметрами
    """

    parser_classes = [MultiPartParser]

    @action(methods=['POST'], detail=False)
    @swagger_auto_schema(
        operation_description='Импорт коллекции через файл',
        manual_parameters=[
            openapi.Parameter('file', openapi.IN_FORM, type=openapi.TYPE_FILE, required=True,
                              description='Файл с данными DegWidget')
        ],
    )
    def import_settings(self, request):
        file = request.FILES.get('file')
        if not file:
            return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            f_data = json.load(file)
            serializer = DegWidgetSerializer(data=f_data, many=True)
            if serializer.is_valid():
                DegWidget.objects().delete()
                serializer.save()
                return Response(serializer.data)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class DegWidgetViewSet(viewsets.ViewSet):

    @staticmethod
    @swagger_auto_schema(
        operation_description='Список всех DegWidget',
    )
    def list(request):
        serializer = DegWidgetSerializer(DegWidget.objects(), many=True)
        return Response(serializer.data)

    @staticmethod
    @swagger_auto_schema(
        operation_description='Получить DegWidget по id',
    )
    def retrieve(request, pk=None):
        deg_widget = DegWidget.objects(pk=pk).first()
        if deg_widget is None:
            return Response()
        else:
            serializer = DegWidgetSerializer(deg_widget)
            return Response(serializer.data)

    @staticmethod
    @swagger_auto_schema(
        request_body=DegWidgetSerializer,
        operation_description='Создать DegWidget'
    )
    @parser_classes([JSONParser])
    def create(request):
        serializer = DegWidgetSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    @swagger_auto_schema(
        operation_description='Удалить DegWidget'
    )
    def destroy(request, pk=None):
        deg_widget = DegWidget.objects(pk=pk).first()
        if deg_widget is None:
            return Response()
        else:
            data = DegWidgetSerializer(deg_widget).data
            deg_widget.delete()
            return Response(data)

    @action(methods=['DELETE'], detail=False)
    @swagger_auto_schema(
        operation_description='Удалить все DegWidget'
    )
    def destroy_all(self, request):
        deg_widgets = DegWidget.objects()
        data = DegWidgetSerializer(deg_widgets, many=True).data
        deg_widgets.delete()
        return Response(data)

    @action(methods=['GET'], detail=False)
    @swagger_auto_schema(
        operation_description='Экспорт коллекции с существующими DegWidget'
    )
    def export_settings(self, request):
        serializer = DegWidgetSerializer(DegWidget.objects(), many=True)
        response = Response(serializer.data, content_type='application/json')
        response['Content-Disposition'] = 'attachment; filename="export_settings.json"'
        return response

    @action(methods=['GET'], detail=False)
    @swagger_auto_schema(
        operation_description='Обновление коллекции DegWidget данными из ClickHouse',
        manual_parameters=[
            openapi.Parameter('schema', openapi.IN_QUERY, type=openapi.TYPE_STRING, required=True,
                              description='Схема в ClickHouse')
        ],
    )
    def create_from_clickhouse(self, request):
        schema = request.GET.get('schema')
        if not schema:
            return Response({'error': 'No schema provided'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = DegWidgetSerializer(DegDataService().update_deg_widgets_collection(request.GET.get('schema')),
                                         many=True)
        return Response(serializer.data)

    @action(methods=['GET'], detail=False)
    @swagger_auto_schema(
        operation_description='Получение данных DegWidget из ClickHouse',
        manual_parameters=[
            openapi.Parameter('schema', openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Схема в ClickHouse'),
            openapi.Parameter('alias', openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description='Псевдоним таблицы в ClickHouse'),
            openapi.Parameter('date_from', openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description='Дата начала промежутка'),
            openapi.Parameter('date_to', openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description='Дата конца промежутка'),
            openapi.Parameter('extractor_code', openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description='Способ выгрузки данных'),
        ],
    )
    def get_board_data(self, request):
        schema = request.GET.get('schema')
        alias = request.GET.get('alias')
        deg_data_service = DegDataService()
        if alias:
            if not schema:
                return Response({'error': 'No schema provided with alias'}, status=status.HTTP_400_BAD_REQUEST)
            return Response(deg_data_service.get_data(schema, alias, DegTypes.BOARD,
                                                      request.GET.get('date_from'),
                                                      request.GET.get('date_to'),
                                                      request.GET.get('extractor_code')).to_dict())
        else:
            widgets = DegWidget.objects(schema=schema, type=DegTypes.BOARD) if schema else DegWidget.objects(type=DegTypes.BOARD)
            res = (deg_data_service.get_data(w.schema, w.alias, DegTypes.BOARD, request.GET.get('date_from'),
                                             request.GET.get('date_to'), request.GET.get('extractor_code')).to_dict()
                   for w in widgets)
            return Response(res)

    @action(methods=['GET'], detail=False)
    @swagger_auto_schema(
        operation_description='Получение отчета из данных ClickHouse',
        manual_parameters=[
            openapi.Parameter('schema', openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Схема в ClickHouse'),
            openapi.Parameter('date_from', openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description='Дата начала промежутка'),
            openapi.Parameter('date_to', openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description='Дата конца промежутка'),
        ],
    )
    def get_deg_report(self, request):
        with io.BytesIO() as output:
            DegDataService().get_deg_report(request.GET.get('date_from'), request.GET.get('date_to'),
                                            request.GET.get('schema')).save(output)
            output.seek(0)
            file_name = f'ДЭГ_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx'
            response = HttpResponse(output.read(),
                                    content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = f'attachment; filename*=UTF-8\'\'{quote(file_name)}'
        return response
