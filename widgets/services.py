import logging
from copy import copy

from djangoProject.settings import clickhouse_default_client
from widgets.models import DegWidget, DegTypes, DegField
from widgets.utils import Utils, ResponseObject


class DegDataService:
    def __init__(self, client=clickhouse_default_client):
        self.__client = client

    def update_deg_widgets_collection(self, schema):
        deg_widgets = list(DegWidget.objects())
        deg_widget_max_order = max(deg_widgets, key=lambda deg_widget: deg_widget.order,
                                   default=DegWidget(order=1)).order
        for ind, deg_widget in enumerate(deg_widgets):
            deg_widgets[ind] = (deg_widget.table_name, deg_widget.type)
        current_tables = Utils.get_tables_comments(schema, self.__client)
        ok_tables = list()
        for table in list(current_tables):
            try:
                if (table, DegTypes.EXPORT) not in deg_widgets or (table, DegTypes.BOARD) not in deg_widgets:
                    deg_widget_fields = list()
                    current_columns = Utils.get_columns_comments(f'{schema}.{table}', self.__client)
                    for order, column in enumerate(current_columns, 1):
                        deg_field = DegField(name=column,
                                             russian_name=current_columns[column],
                                             show=True,
                                             order=order
                                             )
                        deg_widget_fields.append(deg_field)
                    deg_widget = DegWidget(
                        alias=table.replace('_', ''),
                        deg=schema,
                        order=deg_widget_max_order,
                        russian_name=current_tables[table],
                        show=True,
                        table_name=table,
                        fields_list=deg_widget_fields
                    )
                    if (table, DegTypes.EXPORT) not in deg_widgets:
                        deg_widget_ = copy(deg_widget)
                        deg_widget_.type = DegTypes.EXPORT
                        deg_widget_.save()
                    if (table, DegTypes.BOARD) not in deg_widgets:
                        deg_widget_ = copy(deg_widget)
                        deg_widget_.type = DegTypes.BOARD
                        deg_widget_.save()
                    deg_widget_max_order += 1
                    ok_tables.append(table)
            except Exception as e:
                logging.error(f'Table {table} not proceed. Error: {e}')
        return ok_tables

    @staticmethod
    def __get_meta(schema, alias):
        deg_widget = DegWidget.objects(alias=alias, schema=schema).first()
        meta_info = dict()
        for field in deg_widget.fields_list:
            meta_info[field.name] = field.russian_name
        meta_info['table_alias'] = deg_widget.alias
        if deg_widget.russian_name:
            meta_info['table_russian_name'] = deg_widget.russian_name
        return meta_info

    def get_board_data(self, schema, alias, date, extractor_code):
        # TODO Выгрузка данных из схем ДЭГ
        board_deg_widget = DegWidget.objects(alias=alias, schema=schema, type=DegTypes.BOARD).first()
        if not board_deg_widget:
            raise Exception(f'DegWidget: schema = {schema}, alias = {alias} -- not exists')
        table_name = f'{schema}.{board_deg_widget.table_name}'
        sql = (f'{self.__select_with_fields(board_deg_widget.fields_list)} from {table_name}'
               f'{' where date = {date: Date}' if date else ''} order by date')
        return ResponseObject(
            self.__deg_data_extraction(sql, date, extractor_code),
            self.__get_meta(schema, alias)
        )

    def __deg_data_extraction(self, sql, date, extractor_code):
        if extractor_code == 'for_details':
            data = dict()
            with self.__client.query_rows_stream(sql, parameters={'date': date}) as stream:
                for column_name in stream.source.column_names:
                    if column_name != 'date':
                        data[column_name] = list()
                for row in stream:
                    for i, field_value in enumerate(row):
                        if stream.source.column_names[i] != 'date':
                            data[stream.source.column_names[i]].append({
                                'date': row[stream.source.column_names.index('date')],
                                'value': field_value
                            })
            return data
        else:
            data = list()
            with self.__client.query_rows_stream(sql, parameters={'date': date}) as stream:
                for row in stream:
                    row_data = dict()
                    for i, field_value in enumerate(row):
                        row_data[stream.source.column_names[i]] = field_value
                    data.append(row_data)
            return data

    @staticmethod
    def __select_with_fields(fields):
        sql = 'select '
        if len(fields) == 0:
            sql += '*'
        else:
            sql += fields[0].name
            for field in fields[1:]:
                sql += ', ' + field.name
        return sql
