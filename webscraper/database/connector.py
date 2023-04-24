import psycopg2 as pg
from webscraper.tools.config import config
from sqlalchemy import create_engine, URL


# get config from file
def get_config(file, sec):
    params = config(file, sec)
    return params


# create a connection to the database
def init_engine(filename, section):
    params = get_config(filename, section)
    conn = None

    url_params = URL.create(
        "postgresql+psycopg2",
        username=params.get('user'),
        password=params.get('password'),
        host=params.get('host'),
        database=params.get('database')
    )

    engine = create_engine(url_params)

    return engine


def create_connection(engine):

    try:
        conn = engine.raw_connection()
        cur = conn.cursor()
        cur.execute('SELECT version()')
        db_version = cur.fetchone()
        print(db_version)
        print('Database connection successful.')
    except (Exception, pg.DatabaseError) as err:
        print(err)


# close the connection to the database
def close_connection(conn):
    if conn is not None:
        conn.close()
        print('Database connection closed.')
