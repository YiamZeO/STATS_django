class Utils:
    @staticmethod
    def get_tables_comments(schema, client):
        with client.query_rows_stream(
                'select name, comment from system.tables where database = {current_schema:String}',
                parameters={'current_schema': schema}) as stream:
            res = {row[0]: row[1] for row in stream if row[1]}
            return res

    @staticmethod
    def get_columns_comments(table, client):
        with client.query_rows_stream(f'describe table {table}',
                                      parameters={'current_table': table}) as stream:
            name_index = stream.source.column_names.index('name')
            comment_index = stream.source.column_names.index('comment')
            res = {row[name_index]: row[comment_index] for row in stream if row[comment_index]}
            return res


class ResponseObject:
    def __init__(self, data, meta=None):
        self.data = data
        if meta:
            self.meta = meta

    def to_dict(self):
        return vars(self)
