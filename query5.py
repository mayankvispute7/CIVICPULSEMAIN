import sqlite3
conn = sqlite3.connect('backend/app/civicpulse.db')
res = conn.execute('SELECT cluster_id, centroid_lat, centroid_lon, created_at FROM failure_clusters WHERE title="Waterlogging Cluster - Kothrud-Bavdhan" LIMIT 5').fetchall()
for r in res: print(r)
