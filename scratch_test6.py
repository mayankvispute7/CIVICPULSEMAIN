import sqlite3
conn = sqlite3.connect('backend/app/civicpulse.db')
print(conn.execute('PRAGMA table_info(field_evidence)').fetchall())
