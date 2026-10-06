import sqlite3
conn = sqlite3.connect('backend/app/civicpulse.db')
res = conn.execute('SELECT cluster_id, title, complaint_count, confidence FROM failure_clusters WHERE title LIKE "%Waterlogging Cluster - Kothrud-Bavdhan%"').fetchall()
print(len(res))
for r in res[:5]: print(r)
