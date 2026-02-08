#!/usr/bin/env python3
import sqlite3
from pathlib import Path
DB='auth_app.db'
email='Sauravkr670@gmail.com'
root=Path(__file__).resolve().parents[1]
dbpath=root / DB
if not dbpath.exists():
    print('Database not found:',dbpath)
    raise SystemExit(1)
conn=sqlite3.connect(str(dbpath))
cur=conn.cursor()
print('Before deletion:')
cur.execute('SELECT id, phone, email, verified, created_at FROM users WHERE email=?',(email,))
rows=cur.fetchall()
print(rows)
# delete OTPs for this identifier as well
cur.execute('DELETE FROM otps WHERE identifier=?',(email,))
otp_deleted=conn.total_changes
# delete user
cur.execute('DELETE FROM users WHERE email=?',(email,))
user_deleted=conn.total_changes - otp_deleted
conn.commit()
print('\nDelete summary:')
print('OTP deletions (approx):', otp_deleted)
print('User deletions (approx):', user_deleted)
cur.execute('SELECT id, phone, email FROM users WHERE email=?',(email,))
print('After deletion (should be empty):', cur.fetchall())
cur.close()
conn.close()
