import csv
import io

import psycopg2 as pg
import random as rand
from uuid import uuid4
#import connector


def insert_item_data(engine, items):
    item_id = None

    tuples = [tuple(x) for x in items.to_numpy()]
    cols = ','.join(list(items.columns))
    print(cols)
    query = "INSERT INTO %s(%s) VALUES(%%s,%%s,%%s)" % ('item_details', cols)

    try:
        conn = engine.raw_connection()
        cur = conn.cursor()
        cur.executemany(query, tuples)
        conn.commit()

    except (Exception, pg.DatabaseError) as err:
        print(err)
        conn.rollback()
        cur.close()
        return 1

    print('Data inserted successfully.')
    cur.close()


# insert item_data into table
# TODO remove hard coded values and replace with variables
# def insert_item_data(table, engine, items):
#
#
#     # sql = """INSERT INTO item_details(item_name, item_price, item_url) VALUES(%s) RETURNING item_id;"""
#     item_id = None
#
#     try:
#         conn = engine.raw_connection()
#         with conn.cursor() as cur:
#             s_buf = io.StringIO()
#             writer = csv.writer(s_buf)
#             writer.writerows(items.values)
#             s_buf.seek(0)
#
#             columns = ', '.join('"{}"'.format(col) for col in items.columns)
#             if table.schema:
#                 table_name = '{}.{}'.format(table.schema, table.name)
#             else:
#                 table_name = table.name
#
#             sql = 'COPY {} ({}) FROM STDIN WITH CSV'.format(
#                 table_name, columns)
#             cur.copy_expert(sql=sql, file=s_buf)
#
#     except (Exception, pg.DatabaseError) as err:
#         print(err)
#
#
#
#     return item_id
