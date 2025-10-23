import os, sys, json
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from app.app import app

def test_health():
    c = app.test_client()
    r = c.get('/health')
    assert r.status_code == 200
    data = json.loads(r.data)
    assert data['status'] == 'OK'

def test_create_payment():
    c = app.test_client()
    r = c.post('/api/payments', json={'amount': 1234.56, 'currency': 'LKR'})
    assert r.status_code in (200, 201)
