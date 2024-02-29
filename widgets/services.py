import logging
from copy import copy

from widgets.models import DegWidget, DegTypes, DegField
from widgets.utils import Utils


class DegDataService:
    def __init__(self, client):
        self.__client = client

    def update_deg_widgets_collection(self, schema):
        deg_widgets = list(DegWidget.objects())
        deg_widget_max_order = max(deg_widgets, key=lambda deg_widget: deg_widget.order,
                                   default= DegWidget(order=1)).order
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
