import sqlite3
from pathlib import Path
DB = Path(__file__).resolve().parents[1] / 'db.sqlite3'
conn = sqlite3.connect(str(DB))
cur = conn.cursor()
print('id | balance | typeof(balance)')
for r in cur.execute("SELECT id, balance, typeof(balance) FROM accounts_customuser ORDER BY id"):
    print(f"{r[0]} | {r[1]!r} | {r[2]}")
conn.close()

