from flask import Flask, jsonify, request, render_template
from datetime import datetime
import sqlite3
import os
import random

app = Flask(__name__, template_folder='templates', static_folder='static')

# Read DB path from ENV, default to a writable path in container (/data)
DB_FILE = os.getenv('DB_FILE', '/data/transactions.db')

def init_db():
    os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL,
            currency TEXT,
            status TEXT,
            created_at TEXT
        );''')
init_db()

@app.get('/health')
def health():
    return jsonify(status='OK', service='PayLanka Payment Suite')

@app.get('/api/payments')
def list_payments():
    with sqlite3.connect(DB_FILE) as conn:
        cur = conn.execute('SELECT id, amount, currency, status, created_at FROM payments ORDER BY id DESC')
        rows = cur.fetchall()
    data = [dict(id=r[0], amount=r[1], currency=r[2], status=r[3], created_at=r[4]) for r in rows]
    return jsonify(data)

@app.post('/api/payments')
def create_payment():
    body = request.get_json(silent=True) or {}
    amount = body.get('amount')
    currency = (body.get('currency') or 'LKR').upper()
    if amount is None:
        return jsonify(error='Amount is required'), 400
    status = random.choice(['SUCCESS', 'FAILED', 'PENDING'])
    created_at = datetime.utcnow().isoformat()
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute('INSERT INTO payments (amount, currency, status, created_at) VALUES (?, ?, ?, ?)',
                     (amount, currency, status, created_at))
        conn.commit()
    return jsonify(message='Payment processed', status=status, amount=amount, currency=currency), 201

@app.get('/api/stats')
def stats():
    with sqlite3.connect(DB_FILE) as conn:
        total = conn.execute('SELECT COUNT(*) FROM payments').fetchone()[0]
        succ  = conn.execute('SELECT COUNT(*) FROM payments WHERE status="SUCCESS"').fetchone()[0]
        fail  = conn.execute('SELECT COUNT(*) FROM payments WHERE status="FAILED"').fetchone()[0]
        pend  = conn.execute('SELECT COUNT(*) FROM payments WHERE status="PENDING"').fetchone()[0]
    return jsonify(total=total, success=succ, failed=fail, pending=pend)

@app.get('/')
def home():
    return render_template('index.html', title='PayLanka • Payment Console')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
