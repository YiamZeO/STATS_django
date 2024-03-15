from djangoProject.settings import clickhouse_default_client
from utils.utils import ResponseObject


class PetsService:
    def __init__(self, client=clickhouse_default_client):
        self.__client = client

    def pets_categories(self):
        categories = list()
        sql = 'select distinct category FROM pets_report.categories'
        with self.__client.query_rows_stream(sql) as stream:
            for row in stream:
                categories.append(row[0])
        return ResponseObject(categories)

    def visitors_data(self, date_from, date_to):
        res = dict()
        sql = (f'select * from pets_report.pets_visits {'where date between cast({date_from:String} as Date) '
               'and cast({date_to:String} as Date)' if date_from and date_to else ''} order by date')
        with self.__client.query_rows_stream(sql, parameters={
            'date_from': date_from,
            'date_to': date_to
        }) as stream:
            for column in stream.source.column_names:
                if column != 'date':
                    res[column] = {
                        'data_by_dates': list(),
                        'sum': 0
                    }
            for row in stream:
                for i, column in enumerate(row):
                    if stream.source.column_names[i] != 'date':
                        res[stream.source.column_names[i]]['data_by_dates'].append({
                            'date': row[stream.source.column_names.index('date')],
                            'value': column
                        })
                        res[stream.source.column_names[i]]['sum'] += column
        return ResponseObject(res,
                              {
                                  'visit_mos': "Посетители",
                                  'uniq_visit_mos': 'Уникальные посетители',
                                  'visit_sso': 'Авторизованные посетители',
                                  'uniq_visit_sso': 'Уникальные авторизованные посетители',
                              })
