import sqlite3
conn = sqlite3.connect('backend/app/civicpulse.db')
print(conn.execute('SELECT work_order_id, title FROM work_orders').fetchall())
