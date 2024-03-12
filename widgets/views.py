import json

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from widgets.models import DegWidget
from widgets.serializers import DegWidgetSerializer
from widgets.services import DegDataService


class DegWidgetViewSet(viewsets.ViewSet):

    def list(self, request):
        serializer = DegWidgetSerializer(DegWidget.objects(), many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        deg_widget = DegWidget.objects(pk=pk).first()
        if deg_widget is None:
            return Response()
        else:
            serializer = DegWidgetSerializer(deg_widget)
            return Response(serializer.data)

    def create(self, request):
        serializer = DegWidgetSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        deg_widget = DegWidget.objects(pk=pk).first()
        if deg_widget is None:
            return Response()
        else:
            data = DegWidgetSerializer(deg_widget).data
            deg_widget.delete()
            return Response(data)

    @action(methods=['DELETE'], detail=False)
    def destroy_all(self, request):
        deg_widgets = DegWidget.objects()
        data = DegWidgetSerializer(deg_widgets, many=True).data
        deg_widgets.delete()
        return Response(data)

    @action(methods=['GET'], detail=False)
    def export_settings(self, request):
        serializer = DegWidgetSerializer(DegWidget.objects(), many=True)
        response = Response(serializer.data, content_type='application/json')
        response['Content-Disposition'] = 'attachment; filename="export_settings.json"'
        return response

    @action(methods=['POST'], detail=False)
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

    @action(methods=['GET'], detail=False)
    def create_from_clickhouse(self, request):
        schema = request.GET.get('schema')
        if not schema:
            return Response({'error': 'No schema provided'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(DegDataService().update_deg_widgets_collection(request.GET.get('schema')))

    @action(methods=['GET'], detail=False)
    def get_board_data(self, request):
        schema = request.GET.get('schema')
        alias = request.GET.get('alias')
        deg_data_service = DegDataService()
        if not schema:
            return Response({'error': 'No schema provided'}, status=status.HTTP_400_BAD_REQUEST)
        if alias:
            return Response(deg_data_service.get_board_data(schema, request.GET.get('alias'), request.GET.get('date'),
                                                            request.GET.get('extractor_code')).to_dict())
        else:
            res = list()
            for widget in DegWidget.objects():
                res.append(deg_data_service.get_board_data(schema, widget.alias, request.GET.get('date'),
                                                           request.GET.get('extractor_code')).to_dict())
            return Response(res)
