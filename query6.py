import sqlite3
conn = sqlite3.connect('backend/app/civicpulse.db')
res = conn.execute('SELECT COUNT(DISTINCT title) FROM failure_clusters').fetchall()
print(res)
