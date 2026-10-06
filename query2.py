import sqlite3
conn = sqlite3.connect('backend/app/civicpulse.db')
print(conn.execute('SELECT COUNT(*) FROM failure_clusters').fetchall())
