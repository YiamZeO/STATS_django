from rest_framework import serializers
from widgets.models import DegField, AdditionalExport, DegWidget, DegTypes


def get_created_from_serializer(serializer):
    if serializer.initial_data is None:
        return None
    if serializer.is_valid():
        return serializer.create(serializer.validated_data)
    else:
        raise serializers.ValidationError(serializer.errors)


class DegFieldSerializer(serializers.Serializer):
    name = serializers.CharField(required=True,
                                 error_messages={'DegFieldSerializer error': 'name is required'})
    russian_name = serializers.CharField(required=True,
                                         error_messages={'DegFieldSerializer error': 'russian_name is required'})
    order = serializers.IntegerField(required=True,
                                     error_messages={'DegFieldSerializer error': 'order is required'})
    show = serializers.BooleanField(default=True)

    def create(self, validated_data):
        return DegField(**validated_data)


class AdditionalExportSerializer(serializers.Serializer):
    first = serializers.CharField(required=True,
                                  error_messages={'AdditionalExportSerializer error': 'first is required'})
    second = serializers.CharField(required=True,
                                   error_messages={'AdditionalExportSerializer error': 'second is required'})
    db_column_name = serializers.CharField(required=True,
                     error_messages={'AdditionalExportSerializer error':  'db_column_name is required'})

    def create(self, validated_data):
        return AdditionalExport(**validated_data)


class DegWidgetSerializer(serializers.Serializer):
    id = serializers.CharField(required=False)
    alias = serializers.CharField(error_messages={'DegWidgetSerializer error': 'alias is required'})
    schema = serializers.CharField(error_messages={'DegWidgetSerializer error': 'schema is required'})
    order = serializers.IntegerField(error_messages={'DegWidgetSerializer error': 'order is required'})
    russian_name = serializers.CharField(required=False)
    show = serializers.BooleanField(error_messages={'DegWidgetSerializer error': 'show is required'})
    table_name = serializers.CharField(error_messages={'DegWidgetSerializer error': 'table_name is required'})
    img = serializers.CharField(required=False)
    type = serializers.CharField(error_messages={'DegWidgetSerializer error': 'type is required'})
    fields_list = serializers.ListField(error_messages={'DegWidgetSerializer error': 'fields_list is required'})
    additional_export = serializers.JSONField(required=False)

    def create(self, validated_data):
        validated_data['type'] = DegTypes(validated_data.get('type').upper())

        deg_field_serializer = DegFieldSerializer(data=validated_data.get('fields_list'), many=True)
        validated_data['fields_list'] = get_created_from_serializer(deg_field_serializer)

        additional_export_serializer = AdditionalExportSerializer(data=validated_data.get('additional_export'))
        validated_data['additional_export'] = get_created_from_serializer(additional_export_serializer)

        return DegWidget(**validated_data).save()

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['fields_list'] = DegFieldSerializer(instance.fields_list, many=True).data
        if ret['additional_export'] is not None:
            ret['additional_export'] = AdditionalExportSerializer(instance.additional_export).data
        else:
            ret.pop('additional_export')
        if ret['img'] is None:
            ret.pop('img')
        ret['type'] = instance.type.name
        return ret
