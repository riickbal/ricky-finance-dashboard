#!/usr/bin/env python3
"""
backup.py — Export finance DB ke JSON lokal.
Run: python3 backup.py
Output: ../backup/finance_backup.json (tidak di-push ke GitHub)
"""
import sqlite3, json, os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), 'finance.db')
OUT_DIR  = os.path.join(os.path.dirname(__file__), '..', 'backup')
OUT_PATH = os.path.join(OUT_DIR, 'finance_backup.json')

os.makedirs(OUT_DIR, exist_ok=True)

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row

def q(sql):
    return [dict(r) for r in conn.execute(sql).fetchall()]

data = {
    'exported_at': datetime.now().isoformat(),
    'transactions': q('SELECT * FROM transactions ORDER BY date DESC'),
    'banks':        q('SELECT * FROM banks'),
    'credit_cards': q('SELECT * FROM credit_cards'),
    'loans':        q('SELECT * FROM loans'),
    'fixed_assets': q('SELECT * FROM fixed_assets'),
    'investments':  q('SELECT * FROM investments'),
    'config':       {r['key']: r['value'] for r in conn.execute('SELECT key, value FROM config').fetchall()},
}
conn.close()

with open(OUT_PATH, 'w') as f:
    json.dump(data, f, ensure_ascii=False, indent=2, default=str)

print(f"✅ Backup saved: {OUT_PATH}")
print(f"   Transactions : {len(data['transactions'])}")
print(f"   Banks        : {len(data['banks'])}")
print(f"   Fixed Assets : {len(data['fixed_assets'])}")
