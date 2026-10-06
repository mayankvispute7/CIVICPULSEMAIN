import sqlite3
conn = sqlite3.connect('backend/app/civicpulse.db')
print(conn.execute("SELECT intervention_id FROM intervention_options WHERE case_id='000e8866-a354-414a-9714-1c603abc59f6' LIMIT 1").fetchone()[0])
