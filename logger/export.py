import sys
from datetime import date, timedelta
import db

def export_all(filename: str):
    db.export_table('data', filename)

def archive(filename: str):
    # TODO: consider timezone
    to_date = date.today() - timedelta(days=2)
    db.archive_rows_before_date('data', filename, to_date)

if __name__ == '__main__':
    filename = 'data.csv'
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    #export_all(filename)
    archive(filename)
