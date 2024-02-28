import json

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from widgets.models import DegWidget
from widgets.serializers import DegWidgetSerializer


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
            serializer = DegWidgetSerializer(deg_widget)
            deg_widget.delete()
            return Response(serializer.data)

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
