
from datetime import date, datetime, timedelta
import os

from dotenv import load_dotenv

import sqlite3
import pandas as pd

load_dotenv()

LOG_DB_NAME = os.getenv('LOG_DB_NAME')
# TODO: use this table
LOG_DB_TABLE = os.getenv('LOG_DB_TABLE')

def get_connection():
    conn_name = os.path.join(os.path.dirname(os.path.abspath(__file__)), LOG_DB_NAME)
    print(conn_name)
    return sqlite3.connect(conn_name)

def insert(table: str, t: datetime, topic: str, value: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(f"INSERT INTO {table} (t, topic, value) VALUES (?, ?, ?)", (
        t.isoformat(),
        topic,
        value))
    conn.commit()
    conn.close()
    return True


def fetchall(table: str, start: datetime = None):
    conn = get_connection()
    cur = conn.cursor()
    if start:
        cur.execute(f"SELECT * FROM {table} WHERE t >= ?", (start,))
    else:
        cur.execute(f"SELECT * FROM {table}")
    ret = [(datetime.fromisoformat(t), topic, float(value)) for (t, topic, value) in cur.fetchall()]
    conn.close()
    return ret

def export_table(table: str, filename: str):
    conn_name = os.path.join(os.path.dirname(os.path.abspath(__file__)), LOG_DB_NAME)
    conn = sqlite3.connect(conn_name, isolation_level=None, detect_types=sqlite3.PARSE_COLNAMES)
    db_df = pd.read_sql_query(f"SELECT * FROM {table}", conn)
    db_df.to_csv(filename, index=False)

def archive_rows_before_date(table: str, filename: str, to_date: date):
    to_datetime = datetime(to_date.year, to_date.month, to_date.day + 1, 0, 0, 0, 0)
    conn_name = os.path.join(os.path.dirname(os.path.abspath(__file__)), LOG_DB_NAME)
    conn = sqlite3.connect(conn_name, isolation_level=None, detect_types=sqlite3.PARSE_COLNAMES)
    db_df = pd.read_sql_query(f"SELECT * FROM {table} WHERE t < ?", conn, params=(to_datetime,))
    db_df.to_csv(filename, index=False)

    conn.cursor().execute(f"DELETE FROM {table} WHERE t < ?", (to_datetime,))
    conn.close()

if __name__ == '__main__':
    print('create DB and migrate if needed')
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('CREATE TABLE data (t datetime, topic varchar, value float)')
    conn.close()

    #insert("data", datetime.now(), "ogiiot/data/test", 123)

    #result = fetchall('data', start=datetime.now()- timedelta(hours=24))
    #print(result)
