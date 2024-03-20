from typing import Final

from djangoProject.settings import clickhouse_default_client
from utils.utils import ResponseObject


class PetsService:

    @property
    def schema(self):
        return self.__schema

    def __init__(self, client=clickhouse_default_client):
        self.__client = client
        self.__schema: Final = 'pets_report'

    def pets_categories(self):
        sql = f'select distinct category FROM {self.__schema}.categories'
        with self.__client.query_rows_stream(sql) as stream:
            categories = [row[0] for row in stream]
        return ResponseObject(categories)

    def visitors_data(self, date_from, date_to):
        sql = f'''select * from {self.__schema}.pets_visits {('where date between cast({date_from:String} as Date) '
              'and cast({date_to:String} as Date)') if date_from and date_to else ''} order by date'''
        with self.__client.query_rows_stream(sql, parameters={
            'date_from': date_from,
            'date_to': date_to
        }) as stream:
            res = {column: {
                'data_by_dates': list(),
                'sum': 0
            }
                for column in stream.source.column_names if column != 'date'}
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

    def get_transitions_and_actions_data(self, date_from, date_to, category):
        all_transitions_service = 'Жизненные ситуации, всего переходов' if category == 'Жизненные ситуации' else (
            'Сведения о моих питомцах, всего переходов' if category == 'Сведения о моих питомцах' else None)
        with self.__client.query_rows_stream(f'select service from {self.__schema}.categories '
                                             'where category = {category:String}',
                                             parameters={'category': category}) as stream:
            services = [row[stream.source.column_names.index('service')] for row in stream
                        if row[stream.source.column_names.index('service')] != all_transitions_service]
        data_table = 'pets_events' if category == 'Действия' else 'pets_actions'
        sql = f'''select * from {self.__schema}.{data_table} where {('(date between {date_from:String} and '
              '{date_to:String}) and ') if date_from and date_to else ''}(service = \'{services[0]}\''''
        if len(services) > 1:
            or_services = [f' or service = \'{service}\'' for service in services[1:]]
            sql += ''.join(or_services)
        sql += ') order by date'
        if all_transitions_service:
            services.append(all_transitions_service)
        res = {service: {
            'data_by_dates': list(),
            'sum': 0
        } for service in services}
        with self.__client.query_rows_stream(sql, parameters={
            'date_from': date_from,
            'date_to': date_to
        }) as stream:
            for row in stream:
                date_value = {'date': row[stream.source.column_names.index('date')],
                              'value': row[stream.source.column_names.index('count')]}
                res[row[stream.source.column_names.index('service')]]['data_by_dates'].append(date_value)
                res[row[stream.source.column_names.index('service')]]['sum'] += date_value['value']
        if all_transitions_service:
            sql = (f'''select date, sum(count) as count from {self.__schema}.pets_actions t1 join 
                   {self.__schema}.categories t2 on t1.service = t2.service 
                   where{' (date between {date_from:String} and {date_to:String}) and' if date_from and date_to 
                   else ''} '''
                   'category = {category:String} group by date')
            with self.__client.query_rows_stream(sql, parameters={
                'date_from': date_from,
                'date_to': date_to,
                'category': category
            }) as stream:
                for row in stream:
                    date_value = {'date': row[stream.source.column_names.index('date')],
                                  'value': row[stream.source.column_names.index('count')]}
                    res[all_transitions_service]['data_by_dates'].append(date_value)
                    res[all_transitions_service]['sum'] += date_value['value']
        res = [{
            'service': service,
            'data_by_dates': data['data_by_dates'],
            'sum': data['sum']
        } for service, data in res.items()]
        return ResponseObject(res, {
            'category': category
        })
