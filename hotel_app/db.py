from contextlib import contextmanager

import pymysql
from pymysql.cursors import DictCursor

from .config import DB_CONFIG


@contextmanager
def connection(dict_rows=False):
    options = dict(DB_CONFIG)
    if dict_rows:
        options["cursorclass"] = DictCursor
    conn = pymysql.connect(**options)
    try:
        yield conn
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def fetch_all(sql, params=(), dict_rows=False):
    with connection(dict_rows) as conn, conn.cursor() as cursor:
        cursor.execute(sql, params) if params else cursor.execute(sql)
        return cursor.fetchall()


def fetch_one(sql, params=(), dict_rows=False):
    with connection(dict_rows) as conn, conn.cursor() as cursor:
        cursor.execute(sql, params) if params else cursor.execute(sql)
        return cursor.fetchone()


def execute(sql, params=()):
    with connection() as conn, conn.cursor() as cursor:
        cursor.execute(sql, params) if params else cursor.execute(sql)
        conn.commit()
        return cursor.lastrowid
