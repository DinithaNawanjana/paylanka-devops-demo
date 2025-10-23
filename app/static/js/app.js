const $ = (sel) => document.querySelector(sel);
const API = {
  health: '/health',
  payments: '/api/payments',
  stats: '/api/stats'
};

function fmt(n) { return Number(n).toLocaleString(); }

async function fetchJSON(url, opts={}) {
  const res = await fetch(url, Object.assign({ headers: { 'Content-Type': 'application/json' } }, opts));
  return res.json();
}

async function refreshKPIs() {
  const s = await fetchJSON(API.stats);
  #kpi-total.textContent = fmt(s.total || 0);
  #kpi-success.textContent = fmt(s.success || 0);
  #kpi-failed.textContent = fmt(s.failed || 0);
}

function badge(status) {
  const map = {
    'SUCCESS': 'badge badge-success',
    'FAILED': 'badge badge-failed',
    'PENDING': 'badge badge-pending'
  };
  const cls = map[status] || 'badge';
  return <span class=''></span>;
}

async function refreshTable() {
  const list = await fetchJSON(API.payments);
  const tbody = #paymentsTable;
  tbody.innerHTML = list.map(p => 
    <tr>
      <td class='td'>#</td>
      <td class='td'></td>
      <td class='td'></td>
      <td class='td'></td>
      <td class='td text-slate-400'></td>
    </tr>
  ).join('');
}

async function checkHealth() {
  try {
    const h = await fetchJSON(API.health);
    #statusBadge.textContent = h.status === 'OK' ? 'healthy' : 'degraded';
  } catch {
    #statusBadge.textContent = 'offline';
  }
}

async function submitPayment(e) {
  e.preventDefault();
  const form = e.currentTarget;
  const amount = parseFloat(form.amount.value);
  const currency = form.currency.value;
  const msg = #formMessage;
  if (!amount || amount <= 0) { msg.textContent = 'Enter a valid amount'; msg.style.color='#fb7185'; return; }

  msg.textContent = 'Processing...';
  msg.style.color = '#93c5fd';

  const res = await fetchJSON(API.payments, {
    method: 'POST',
    body: JSON.stringify({ amount, currency })
  });

  if (res.error) {
    msg.textContent = 'Error: ' + res.error;
    msg.style.color = '#fb7185';
  } else {
    msg.textContent = Status:  •  ;
    msg.style.color = res.status === 'SUCCESS' ? '#34d399' : (res.status === 'FAILED' ? '#fb7185' : '#fbbf24');
    form.reset();
    await Promise.all([refreshKPIs(), refreshTable()]);
  }
}

document.addEventListener('DOMContentLoaded', async () => {
  #year.textContent = new Date().getFullYear();
  #paymentForm.addEventListener('submit', submitPayment);
  await Promise.all([checkHealth(), refreshKPIs(), refreshTable()]);
  setInterval(() => { checkHealth(); refreshKPIs(); }, 8000);
});
