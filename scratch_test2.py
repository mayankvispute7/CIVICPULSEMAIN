import sqlite3
conn = sqlite3.connect('backend/app/civicpulse.db')
print(len(conn.execute('SELECT * FROM work_order_tasks').fetchall()))
