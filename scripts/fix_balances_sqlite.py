from decimal import Decimal, InvalidOperation
import sqlite3
from pathlib import Path

DB = Path(__file__).resolve().parents[1] / 'db.sqlite3'
if not DB.exists():
    print('db.sqlite3 not found at', DB)
    raise SystemExit(1)

max_digits = 10
decimal_places = 2
max_allowed = Decimal(10) ** (max_digits - decimal_places)

conn = sqlite3.connect(str(DB))
cur = conn.cursor()
cur.execute("SELECT id, balance FROM accounts_customuser")
rows = cur.fetchall()

bad = []
for id_, balance in rows:
    try:
        dec = Decimal(str(balance))
    except (InvalidOperation, TypeError, ValueError):
        bad.append((id_, balance, 'invalid'))
        continue
    try:
        if abs(dec) >= max_allowed:
            bad.append((id_, balance, 'out_of_range'))
    except Exception as e:
        bad.append((id_, balance, f'error:{e}'))

if not bad:
    print('No invalid balances found.')
else:
    print('Found bad rows:')
    for item in bad:
        print(item)
    for id_, _bal, _reason in bad:
        cur.execute("UPDATE accounts_customuser SET balance = ? WHERE id = ?", ("0.00", id_))
    conn.commit()
    print('Fixed ids:', [i[0] for i in bad])

print('\nCurrent rows:')
cur.execute("SELECT id, balance, typeof(balance) FROM accounts_customuser")
for r in cur.fetchall():
    print(r)

conn.close()

