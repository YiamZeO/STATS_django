class Utils:
    """
    Класс утилит
    """

    @staticmethod
    def get_tables_comments(schema, client):
        """
        Получение словаря таблиц и их комментариев из ClickHouse
        :param schema: схема в ClickHouse
        :param client: ClickHouse клиент
        :return: словарь таблиц и их комментариев из ClickHouse
        """

        with client.query_rows_stream(
                'select name, comment from system.tables where database = {current_schema:String}',
                parameters={'current_schema': schema}) as stream:
            res = {row[0]: row[1] for row in stream if row[1]}
            return res

    @staticmethod
    def get_columns_comments(table, client):
        """
        Получение словаря столбцов и их комментариев из ClickHouse
        :param table: таблица в ClickHouse
        :param client: ClickHouse клиент
        :return: словарь столбцов и их комментариев из ClickHouse
        """

        with client.query_rows_stream(f'describe table {table}',
                                      parameters={'current_table': table}) as stream:
            name_index = stream.source.column_names.index('name')
            comment_index = stream.source.column_names.index('comment')
            res = {row[name_index]: row[comment_index] for row in stream if row[comment_index]}
            return res


class ResponseObject:
    """
    Класс ответа для запросов:
    \n data -- данные
    \n meta -- мета данные
    """

    def __init__(self, data, meta=None):
        self.data = data
        if meta:
            self.meta = meta

    def to_dict(self):
        """
        Преобразование ответа в словарь
        :return: словарь ответа
        """

        return vars(self)
