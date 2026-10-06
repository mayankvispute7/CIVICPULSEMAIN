import sqlite3
conn = sqlite3.connect('backend/app/civicpulse.db')
print(conn.execute("SELECT * FROM resolution_plans WHERE case_id='f271b76e-5a73-402a-b237-2718c352bf8f'").fetchall())
