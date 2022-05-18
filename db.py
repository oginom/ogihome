
from datetime import datetime, timedelta

import sqlite3

DB_NAME = 'ogiiot.db'
DB_TABLE = 'raw_data'


def insert(table, t, topic, value):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute(f"INSERT INTO {table} (t, topic, value) VALUES (?, ?, ?)", (
        t.isoformat(),
        topic,
        value))
    conn.commit()
    conn.close()
    return True


def fetchall(table, start=None):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    if start:
        cur.execute(f"SELECT * FROM {table} WHERE t >= ?", (start,))
    else:
        cur.execute(f"SELECT * FROM {table}")
    ret = [(datetime.fromisoformat(t), topic, float(value)) for (t, topic, value) in cur.fetchall()]
    conn.close()
    return ret

if __name__ == '__main__':
    print('create DB and migrate if needed')
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute('CREATE TABLE data (t datetime, topic varchar, value float)')
    conn.close()

    #insert("data", datetime.now(), "ogiiot/data/test", 123)

    #result = fetchall('data', start=datetime.now()- timedelta(hours=24))
    #print(result)
