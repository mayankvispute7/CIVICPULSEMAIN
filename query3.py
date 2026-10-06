import sqlite3
conn = sqlite3.connect('backend/app/civicpulse.db')
print('Complaints:', conn.execute('SELECT COUNT(*) FROM complaints').fetchall()[0][0])
print('Clusters:', conn.execute('SELECT COUNT(*) FROM failure_clusters').fetchall()[0][0])
