import sqlite3
conn = sqlite3.connect('backend/app/civicpulse.db')
print(conn.execute('SELECT cluster_id, title, complaint_count FROM failure_clusters LIMIT 5').fetchall())
