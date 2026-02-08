#!/usr/bin/env python3
import sqlite3
from pathlib import Path
root=Path(__file__).resolve().parents[1]
dbpath=root / 'auth_app.db'
if not dbpath.exists():
    print('Database not found:',dbpath)
    raise SystemExit(1)
conn=sqlite3.connect(str(dbpath))
cur=conn.cursor()
cur.execute('SELECT id, phone, email, verified, created_at FROM users ORDER BY id')
rows=cur.fetchall()
print('Users:')
for r in rows:
    print(r)
cur.close()
conn.close()
