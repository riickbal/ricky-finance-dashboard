// ============================================================
// server.js — Ricky Finance Dashboard API
// Run: node server.js
// Port: 3000
// ============================================================

const express = require('express');
const cors    = require('cors');
const path    = require('path');
const { DatabaseSync } = require('node:sqlite');

const app  = express();
const PORT = process.env.PORT || 3000;
const db   = new DatabaseSync(path.join(__dirname, 'finance.db'));

// Middleware
app.use(cors());
app.use(express.json());

// Serve dashboard static files (index.html, data.js, dll)
app.use(express.static(path.join(__dirname, '..')));

// ============================================================
// HELPER — build full dashboard payload (same shape as data.js)
// ============================================================
function buildDashboardPayload() {
  // Config
  const configRows = db.prepare('SELECT key, value FROM config').all();
  const config = {};
  for (const row of configRows) config[row.key] = row.value;

  // Banks
  const banks = db.prepare('SELECT * FROM banks').all().map(b => ({
    name: b.name, nick: b.nick, cat: b.cat, type: b.type,
    acct: b.acct, balance: b.balance, updated: b.updated, notes: b.notes
  }));

  // Credit cards
  const creditCards = db.prepare('SELECT * FROM credit_cards').all().map(cc => ({
    name: cc.name, issuer: cc.issuer, limit: cc.limit_amt,
    outstanding: cc.outstanding, dueDate: cc.due_date, notes: cc.notes
  }));

  // Loans
  const loans = db.prepare('SELECT * FROM loans').all().map(l => ({
    type: l.type, lender: l.lender, remaining: l.remaining,
    monthly: l.monthly, rate: l.rate, tenor: l.tenor, notes: l.notes
  }));

  // Investments
  const investments = db.prepare('SELECT * FROM investments').all().map(inv => ({
    platform: inv.platform, ticker: inv.ticker, type: inv.type,
    qty: inv.qty, avgBuy: inv.avg_buy, currency: inv.currency,
    costBasis: inv.cost_basis, currentPrice: inv.current_price,
    platformCash: inv.platform_cash, nbvOverride: inv.nbv_override,
    lastUpdate: inv.last_update, notes: inv.notes
  }));

  // Fixed assets
  const fixedAssets = db.prepare('SELECT * FROM fixed_assets').all().map(fa => ({
    id: fa.id, name: fa.name, category: fa.category,
    purchaseDate: fa.purchase_date, cost: fa.cost,
    usefulLifeMonths: fa.useful_life_months,
    transactionRef: fa.transaction_ref, notes: fa.notes
  }));

  // Receivables
  const receivables = db.prepare('SELECT * FROM receivables').all().map(r => ({
    id: r.id, name: r.name, amount: r.amount, date: r.date,
    dueDate: r.due_date, notes: r.notes, status: r.status, settledOn: r.settled_on
  }));

  // Transactions
  const transactions = db.prepare('SELECT * FROM transactions ORDER BY date DESC, created_at DESC').all().map(t => ({
    id: t.id, date: t.date, type: t.type, category: t.category,
    account: t.account, amount: t.amount, desc: t.desc
  }));

  // Budgets
  const budgetRows = db.prepare('SELECT * FROM budgets').all();
  const budgets = {};
  for (const b of budgetRows) budgets[b.category] = b.amount;

  return {
    fxRate: parseFloat(config.fxRate) || 17950,
    lastUpdated: config.lastUpdated || new Date().toISOString().split('T')[0],
    banks, creditCards, loans, investments, fixedAssets, receivables,
    transactions, budgets,
    income: {
      salary: parseFloat(config.salary) || 0,
      kprMonthly: parseFloat(config.kprMonthly) || 0
    }
  };
}

// ============================================================
// HELPER — generate next transaction ID
// ============================================================
function nextTrxId() {
  const row = db.prepare("SELECT id FROM transactions ORDER BY CAST(SUBSTR(id,2) AS INTEGER) DESC LIMIT 1").get();
  if (!row) return 't1';
  const num = parseInt(row.id.replace('t', '')) + 1;
  return `t${num}`;
}

// ============================================================
// GET /api/data — full dashboard payload
// ============================================================
app.get('/api/data', (req, res) => {
  try {
    res.json(buildDashboardPayload());
  } catch (e) {
    console.error(e);
    res.status(500).json({ error: e.message });
  }
});

// ============================================================
// GET /api/banks — bank balances only
// ============================================================
app.get('/api/banks', (req, res) => {
  try {
    const banks = db.prepare('SELECT nick, name, cat, type, balance, updated, notes FROM banks').all();
    const total = banks.reduce((s, b) => s + (b.balance || 0), 0);
    res.json({ banks, totalCash: total });
  } catch (e) { res.status(500).json({ error: e.message }); }
});

// ============================================================
// GET /api/creditcards — CC balances + limits only
// ============================================================
app.get('/api/creditcards', (req, res) => {
  try {
    const cards = db.prepare('SELECT name, issuer, limit_amt as limit, outstanding, due_date as dueDate, notes FROM credit_cards').all();
    const totalOutstanding = cards.reduce((s, c) => s + (c.outstanding || 0), 0);
    const totalLimit = cards.reduce((s, c) => s + (c.limit || 0), 0);
    res.json({ cards, totalOutstanding, totalLimit, utilization: totalLimit ? Math.round(totalOutstanding / totalLimit * 100) : 0 });
  } catch (e) { res.status(500).json({ error: e.message }); }
});

// ============================================================
// GET /api/investments — portfolio only
// ============================================================
app.get('/api/investments', (req, res) => {
  try {
    const investments = db.prepare('SELECT platform, ticker, type, qty, avg_buy as avgBuy, currency, cost_basis as costBasis, current_price as currentPrice, platform_cash as platformCash, notes FROM investments').all();
    const totalCost  = investments.reduce((s, i) => s + (i.costBasis || 0), 0);
    res.json({ investments, totalCostBasis: totalCost });
  } catch (e) { res.status(500).json({ error: e.message }); }
});

// ============================================================
// GET /api/loans — cicilan + outstanding
// ============================================================
app.get('/api/loans', (req, res) => {
  try {
    const loans = db.prepare('SELECT type, lender, remaining, monthly, rate, tenor, notes FROM loans').all();
    const totalRemaining = loans.reduce((s, l) => s + (l.remaining || 0), 0);
    const totalMonthly   = loans.reduce((s, l) => s + (l.monthly || 0), 0);
    res.json({ loans, totalRemaining, totalMonthly });
  } catch (e) { res.status(500).json({ error: e.message }); }
});

// ============================================================
// GET /api/budgets — budget alokasi + actual bulan ini
// ============================================================
app.get('/api/budgets', (req, res) => {
  try {
    const budgetRows = db.prepare('SELECT category, amount FROM budgets').all();
    const budgets = {};
    for (const b of budgetRows) budgets[b.category] = b.amount;

    const month = new Date().toISOString().slice(0, 7); // YYYY-MM
    const actualRows = db.prepare(
      "SELECT category, SUM(amount) as actual FROM transactions WHERE type='Out' AND date LIKE ? GROUP BY category"
    ).all(`${month}%`);
    const actual = {};
    for (const r of actualRows) actual[r.category] = r.actual;

    const result = Object.entries(budgets).map(([cat, budget]) => ({
      category: cat, budget, actual: actual[cat] || 0,
      remaining: budget - (actual[cat] || 0),
      overBudget: (actual[cat] || 0) > budget
    }));
    res.json({ budgets: result, month });
  } catch (e) { res.status(500).json({ error: e.message }); }
});

// ============================================================
// GET /api/income?month=YYYY-MM — income transactions
// ============================================================
app.get('/api/income', (req, res) => {
  try {
    const month = req.query.month || new Date().toISOString().slice(0, 7);
    const rows = db.prepare(
      "SELECT id, date, category, account, amount, desc FROM transactions WHERE type='In' AND date LIKE ? ORDER BY date DESC"
    ).all(`${month}%`);
    const total = rows.reduce((s, r) => s + (r.amount || 0), 0);
    res.json({ month, income: rows, totalIncome: total });
  } catch (e) { res.status(500).json({ error: e.message }); }
});

// ============================================================
// GET /api/expenses?month=YYYY-MM — expense transactions
// ============================================================
app.get('/api/expenses', (req, res) => {
  try {
    const month = req.query.month || new Date().toISOString().slice(0, 7);
    const rows = db.prepare(
      "SELECT id, date, category, account, amount, desc FROM transactions WHERE type='Out' AND date LIKE ? ORDER BY date DESC"
    ).all(`${month}%`);
    const total = rows.reduce((s, r) => s + (r.amount || 0), 0);
    const byCategory = {};
    for (const r of rows) byCategory[r.category] = (byCategory[r.category] || 0) + r.amount;
    res.json({ month, expenses: rows, totalExpenses: total, byCategory });
  } catch (e) { res.status(500).json({ error: e.message }); }
});

// ============================================================
// GET /api/summary — net worth + key metrics
// ============================================================
app.get('/api/summary', (req, res) => {
  try {
    const configRows = db.prepare('SELECT key, value FROM config').all();
    const config = {};
    for (const r of configRows) config[r.key] = r.value;
    const netIncome = parseFloat(config.salary) || 0;

    const banks       = db.prepare('SELECT SUM(balance) as total FROM banks').get();
    const cc          = db.prepare('SELECT SUM(outstanding) as out, SUM(limit_amt) as lim FROM credit_cards').get();
    const loans       = db.prepare('SELECT SUM(remaining) as rem, SUM(monthly) as mon FROM loans').get();
    const investments = db.prepare('SELECT SUM(cost_basis) as cost FROM investments').get();

    const totalCash        = banks.total || 0;
    const totalInvestments = investments.cost || 0;
    const totalAssets      = totalCash + totalInvestments;
    const totalLiabilities = (cc.out || 0) + (loans.rem || 0);
    const netWorth         = totalAssets - totalLiabilities;
    const totalMonthly     = loans.mon || 0;
    const dti              = netIncome ? Math.round(totalMonthly / netIncome * 100) : 0;
    const ccUtil           = cc.lim ? Math.round((cc.out || 0) / cc.lim * 100) : 0;

    const month = new Date().toISOString().slice(0, 7);
    const expRow = db.prepare("SELECT SUM(amount) as total FROM transactions WHERE type='Out' AND date LIKE ?").get(`${month}%`);
    const incRow = db.prepare("SELECT SUM(amount) as total FROM transactions WHERE type='In' AND date LIKE ?").get(`${month}%`);
    const cashFlow = (incRow.total || 0) - (expRow.total || 0);

    res.json({
      netWorth, totalAssets, totalLiabilities,
      totalCash, totalInvestments,
      totalCC: cc.out || 0, totalLoans: loans.rem || 0,
      dti, ccUtilization: ccUtil,
      cashFlow, netIncome,
      alerts: [
        ...(dti > 30    ? [`⚠️ DTI ${dti}% > 30% threshold`] : []),
        ...(ccUtil > 70 ? [`⚠️ CC utilization ${ccUtil}% > 70%`] : []),
        ...(cashFlow < 0 ? [`⚠️ Cash flow negatif bulan ini`] : [])
      ]
    });
  } catch (e) { res.status(500).json({ error: e.message }); }
});

// ============================================================
// POST /api/transactions — tambah transaksi baru
// Body: { date, type, category, account, amount, desc }
// ============================================================
app.post('/api/transactions', (req, res) => {
  try {
    const { date, type, category, account, amount, desc } = req.body;
    if (!date || !type || !category || !account || amount == null) {
      return res.status(400).json({ error: 'Missing required fields: date, type, category, account, amount' });
    }
    const id = req.body.id || nextTrxId();
    db.prepare(`
      INSERT OR REPLACE INTO transactions (id, date, type, category, account, amount, desc)
      VALUES (?, ?, ?, ?, ?, ?, ?)
    `).run(id, date, type, category, account, amount, desc || null);

    console.log(`✅ Transaction added: ${id} | ${date} | ${type} | ${category} | ${account} | ${amount}`);
    res.status(201).json({ success: true, id, message: `Transaction ${id} saved` });
  } catch (e) {
    console.error(e);
    res.status(500).json({ error: e.message });
  }
});

// ============================================================
// PATCH /api/banks/:nick — update saldo bank
// Body: { balance, updated? }
// ============================================================
app.patch('/api/banks/:nick', (req, res) => {
  try {
    const { nick } = req.params;
    const { balance, updated } = req.body;
    if (balance == null) return res.status(400).json({ error: 'balance required' });
    const date = updated || new Date().toISOString().split('T')[0];
    db.prepare('UPDATE banks SET balance = ?, updated = ? WHERE nick = ?').run(balance, date, nick);
    console.log(`✅ Bank updated: ${nick} → Rp${balance.toLocaleString('id-ID')}`);
    res.json({ success: true, nick, balance });
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

// ============================================================
// PATCH /api/creditcards/:name — update CC outstanding
// Body: { outstanding }
// ============================================================
app.patch('/api/creditcards/:name', (req, res) => {
  try {
    const { name } = req.params;
    const { outstanding } = req.body;
    if (outstanding == null) return res.status(400).json({ error: 'outstanding required' });
    db.prepare('UPDATE credit_cards SET outstanding = ? WHERE name = ?').run(outstanding, name);
    console.log(`✅ CC updated: ${name} → outstanding Rp${outstanding.toLocaleString('id-ID')}`);
    res.json({ success: true, name, outstanding });
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

// ============================================================
// PATCH /api/investments/:ticker — update harga investasi
// Body: { currentPrice, qty?, platformCash? }
// ============================================================
app.patch('/api/investments/:ticker', (req, res) => {
  try {
    const { ticker } = req.params;
    const { currentPrice, qty, platformCash } = req.body;
    if (currentPrice == null) return res.status(400).json({ error: 'currentPrice required' });
    let sql = 'UPDATE investments SET current_price = ?';
    const params = [currentPrice];
    if (qty != null)          { sql += ', qty = ?';           params.push(qty); }
    if (platformCash != null) { sql += ', platform_cash = ?'; params.push(platformCash); }
    sql += ', last_update = ? WHERE ticker = ?';
    params.push(new Date().toISOString().split('T')[0], ticker);
    db.prepare(sql).run(...params);
    console.log(`✅ Investment updated: ${ticker} → price ${currentPrice}`);
    res.json({ success: true, ticker, currentPrice });
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

// ============================================================
// PATCH /api/fxrate — update kurs USD/IDR
// Body: { fxRate }
// ============================================================
app.patch('/api/fxrate', (req, res) => {
  try {
    const { fxRate } = req.body;
    if (!fxRate) return res.status(400).json({ error: 'fxRate required' });
    db.prepare('INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)').run('fxRate', String(fxRate));
    console.log(`✅ FX Rate updated: ${fxRate}`);
    res.json({ success: true, fxRate });
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

// ============================================================
// PATCH /api/budgets — update budget per category
// Body: { budgets: { "Meals": 1000000, ... } }
// ============================================================
app.patch('/api/budgets', (req, res) => {
  try {
    const { budgets } = req.body;
    if (!budgets) return res.status(400).json({ error: 'budgets object required' });
    const upsert = db.prepare('INSERT OR REPLACE INTO budgets (category, amount) VALUES (?, ?)');
    db.exec('BEGIN');
    for (const [cat, amt] of Object.entries(budgets)) upsert.run(cat, amt);
    db.exec('COMMIT');
    res.json({ success: true, updated: Object.keys(budgets).length });
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

// ============================================================
// GET /api/transactions — query transactions
// Query params: ?month=2026-06 | ?category=Meals | ?limit=50
// ============================================================
app.get('/api/transactions', (req, res) => {
  try {
    const { month, category, type, limit = 100 } = req.query;
    let sql = 'SELECT * FROM transactions WHERE 1=1';
    const params = [];
    if (month)    { sql += ' AND date LIKE ?'; params.push(month + '%'); }
    if (category) { sql += ' AND category = ?'; params.push(category); }
    if (type)     { sql += ' AND type = ?'; params.push(type); }
    sql += ' ORDER BY date DESC LIMIT ?';
    params.push(parseInt(limit));
    const rows = db.prepare(sql).all(...params);
    res.json(rows);
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

// ============================================================
// BANKS CRUD
// ============================================================
app.post('/api/banks', (req, res) => {
  try {
    const { name, nick, cat, type, acct, balance, notes } = req.body;
    if (!name || !nick) return res.status(400).json({ error: 'name and nick required' });
    db.prepare(`
      INSERT INTO banks (name, nick, cat, type, acct, balance, updated, notes)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    `).run(name, nick, cat||'Bank', type||'Tabungan', acct||'', balance||0,
           new Date().toISOString().split('T')[0], notes||null);
    console.log(`✅ Bank created: ${nick}`);
    res.status(201).json({ success: true, nick });
  } catch (e) { res.status(500).json({ error: e.message }); }
});

app.put('/api/banks/:nick', (req, res) => {
  try {
    const { nick } = req.params;
    const { name, cat, type, acct, balance, notes } = req.body;
    db.prepare(`
      UPDATE banks SET name=COALESCE(?,name), cat=COALESCE(?,cat), type=COALESCE(?,type),
      acct=COALESCE(?,acct), balance=COALESCE(?,balance), notes=COALESCE(?,notes),
      updated=? WHERE nick=?
    `).run(name||null, cat||null, type||null, acct||null, balance??null, notes||null,
           new Date().toISOString().split('T')[0], nick);
    console.log(`✅ Bank updated: ${nick}`);
    res.json({ success: true, nick });
  } catch (e) { res.status(500).json({ error: e.message }); }
});

app.delete('/api/banks/:nick', (req, res) => {
  try {
    const { nick } = req.params;
    db.prepare('DELETE FROM banks WHERE nick = ?').run(nick);
    console.log(`🗑️ Bank deleted: ${nick}`);
    res.json({ success: true, nick });
  } catch (e) { res.status(500).json({ error: e.message }); }
});

// ============================================================
// CREDIT CARDS CRUD
// ============================================================
app.post('/api/creditcards', (req, res) => {
  try {
    const { name, issuer, limit, outstanding, dueDate, notes } = req.body;
    if (!name || !issuer) return res.status(400).json({ error: 'name and issuer required' });
    db.prepare(`
      INSERT INTO credit_cards (name, issuer, limit_amt, outstanding, due_date, notes)
      VALUES (?, ?, ?, ?, ?, ?)
    `).run(name, issuer, limit||0, outstanding||0, dueDate||'', notes||null);
    console.log(`✅ CC created: ${name}`);
    res.status(201).json({ success: true, name });
  } catch (e) { res.status(500).json({ error: e.message }); }
});

app.put('/api/creditcards/:name', (req, res) => {
  try {
    const { name } = req.params;
    const { issuer, limit, outstanding, dueDate, notes } = req.body;
    db.prepare(`
      UPDATE credit_cards SET issuer=COALESCE(?,issuer), limit_amt=COALESCE(?,limit_amt),
      outstanding=COALESCE(?,outstanding), due_date=COALESCE(?,due_date),
      notes=COALESCE(?,notes) WHERE name=?
    `).run(issuer||null, limit??null, outstanding??null, dueDate||null, notes||null, name);
    console.log(`✅ CC updated: ${name}`);
    res.json({ success: true, name });
  } catch (e) { res.status(500).json({ error: e.message }); }
});

app.delete('/api/creditcards/:name', (req, res) => {
  try {
    const { name } = req.params;
    db.prepare('DELETE FROM credit_cards WHERE name = ?').run(name);
    console.log(`🗑️ CC deleted: ${name}`);
    res.json({ success: true, name });
  } catch (e) { res.status(500).json({ error: e.message }); }
});

// ============================================================
// INVESTMENTS CRUD
// ============================================================
app.post('/api/investments', (req, res) => {
  try {
    const { platform, ticker, type, qty, avgBuy, currency, costBasis, currentPrice, platformCash, notes } = req.body;
    if (!platform || !ticker) return res.status(400).json({ error: 'platform and ticker required' });
    db.prepare(`
      INSERT INTO investments (platform, ticker, type, qty, avg_buy, currency, cost_basis,
      current_price, platform_cash, last_update, notes)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `).run(platform, ticker, type||'Saham IDX', qty||0, avgBuy||0, currency||'IDR',
           costBasis||0, currentPrice||0, platformCash||0,
           new Date().toISOString().split('T')[0], notes||null);
    console.log(`✅ Investment created: ${ticker}`);
    res.status(201).json({ success: true, ticker });
  } catch (e) { res.status(500).json({ error: e.message }); }
});

app.put('/api/investments/:ticker', (req, res) => {
  try {
    const { ticker } = req.params;
    const { platform, type, qty, avgBuy, currency, costBasis, currentPrice, platformCash, notes } = req.body;
    db.prepare(`
      UPDATE investments SET platform=COALESCE(?,platform), type=COALESCE(?,type),
      qty=COALESCE(?,qty), avg_buy=COALESCE(?,avg_buy), currency=COALESCE(?,currency),
      cost_basis=COALESCE(?,cost_basis), current_price=COALESCE(?,current_price),
      platform_cash=COALESCE(?,platform_cash), notes=COALESCE(?,notes),
      last_update=? WHERE ticker=?
    `).run(platform||null, type||null, qty??null, avgBuy??null, currency||null,
           costBasis??null, currentPrice??null, platformCash??null, notes||null,
           new Date().toISOString().split('T')[0], ticker);
    console.log(`✅ Investment updated: ${ticker}`);
    res.json({ success: true, ticker });
  } catch (e) { res.status(500).json({ error: e.message }); }
});

app.delete('/api/investments/:ticker', (req, res) => {
  try {
    const { ticker } = req.params;
    db.prepare('DELETE FROM investments WHERE ticker = ?').run(ticker);
    console.log(`🗑️ Investment deleted: ${ticker}`);
    res.json({ success: true, ticker });
  } catch (e) { res.status(500).json({ error: e.message }); }
});

// ============================================================
// LOANS CRUD
// ============================================================
app.post('/api/loans', (req, res) => {
  try {
    const { type, lender, remaining, monthly, rate, tenor, notes } = req.body;
    if (!type || !lender) return res.status(400).json({ error: 'type and lender required' });
    db.prepare(`
      INSERT INTO loans (type, lender, remaining, monthly, rate, tenor, notes)
      VALUES (?, ?, ?, ?, ?, ?, ?)
    `).run(type, lender, remaining||0, monthly||0, rate||0, tenor||0, notes||null);
    console.log(`✅ Loan created: ${type} - ${lender}`);
    res.status(201).json({ success: true, type });
  } catch (e) { res.status(500).json({ error: e.message }); }
});

app.put('/api/loans/:type', (req, res) => {
  try {
    const { type } = req.params;
    const { lender, remaining, monthly, rate, tenor, notes } = req.body;
    db.prepare(`
      UPDATE loans SET lender=COALESCE(?,lender), remaining=COALESCE(?,remaining),
      monthly=COALESCE(?,monthly), rate=COALESCE(?,rate), tenor=COALESCE(?,tenor),
      notes=COALESCE(?,notes) WHERE type=?
    `).run(lender||null, remaining??null, monthly??null, rate??null, tenor??null, notes||null, type);
    console.log(`✅ Loan updated: ${type}`);
    res.json({ success: true, type });
  } catch (e) { res.status(500).json({ error: e.message }); }
});

app.delete('/api/loans/:type', (req, res) => {
  try {
    const { type } = req.params;
    db.prepare('DELETE FROM loans WHERE type = ?').run(type);
    console.log(`🗑️ Loan deleted: ${type}`);
    res.json({ success: true, type });
  } catch (e) { res.status(500).json({ error: e.message }); }
});

// ============================================================
// BUDGET DELETE (create/update via PATCH /api/budgets)
// ============================================================
app.delete('/api/budgets/:category', (req, res) => {
  try {
    const cat = decodeURIComponent(req.params.category);
    db.prepare('DELETE FROM budgets WHERE category = ?').run(cat);
    console.log(`🗑️ Budget deleted: ${cat}`);
    res.json({ success: true, category: cat });
  } catch (e) { res.status(500).json({ error: e.message }); }
});

// ============================================================
// TRANSACTIONS — DELETE & UPDATE
// ============================================================
app.put('/api/transactions/:id', (req, res) => {
  try {
    const { id } = req.params;
    const { date, type, category, account, amount, desc } = req.body;
    db.prepare(`
      UPDATE transactions SET date=COALESCE(?,date), type=COALESCE(?,type),
      category=COALESCE(?,category), account=COALESCE(?,account),
      amount=COALESCE(?,amount), desc=COALESCE(?,desc) WHERE id=?
    `).run(date||null, type||null, category||null, account||null, amount??null, desc||null, id);
    console.log(`✅ Transaction updated: ${id}`);
    res.json({ success: true, id });
  } catch (e) { res.status(500).json({ error: e.message }); }
});

app.delete('/api/transactions/:id', (req, res) => {
  try {
    const { id } = req.params;
    db.prepare('DELETE FROM transactions WHERE id = ?').run(id);
    console.log(`🗑️ Transaction deleted: ${id}`);
    res.json({ success: true, id });
  } catch (e) { res.status(500).json({ error: e.message }); }
});

// ============================================================
// GET /api/receivables — piutang
// ============================================================
app.get('/api/receivables', (req, res) => {
  try {
    const rows = db.prepare('SELECT * FROM receivables ORDER BY due_date ASC').all();
    const active   = rows.filter(r => r.status !== 'settled');
    const settled  = rows.filter(r => r.status === 'settled');
    const totalActive = active.reduce((s, r) => s + (r.amount || 0), 0);
    res.json({ receivables: rows, active, settled, totalActive });
  } catch (e) { res.status(500).json({ error: e.message }); }
});

// ============================================================
// GET /api/fixed-assets — aset tetap (properti, kendaraan, dll)
// ============================================================
app.get('/api/fixed-assets', (req, res) => {
  try {
    const rows = db.prepare('SELECT * FROM fixed_assets').all();
    const now = new Date();
    const assets = rows.map(fa => {
      const purchaseDate = new Date(fa.purchase_date);
      const monthsOwned  = Math.floor((now - purchaseDate) / (1000 * 60 * 60 * 24 * 30));
      const accumulated  = fa.useful_life_months > 0
        ? Math.min(fa.cost, (fa.cost / fa.useful_life_months) * monthsOwned) : 0;
      const bookValue = fa.cost - accumulated;
      return { ...fa, monthsOwned, bookValue: Math.round(bookValue) };
    });
    const totalBookValue = assets.reduce((s, a) => s + a.bookValue, 0);
    res.json({ fixedAssets: assets, totalBookValue });
  } catch (e) { res.status(500).json({ error: e.message }); }
});

// ============================================================
// GET /api/expenses/compare?month1=YYYY-MM&month2=YYYY-MM
// ============================================================
app.get('/api/expenses/compare', (req, res) => {
  try {
    const now = new Date();
    const thisMonth = now.toISOString().slice(0, 7);
    const lastMonth = new Date(now.getFullYear(), now.getMonth() - 1).toISOString().slice(0, 7);
    const month1 = req.query.month1 || lastMonth;
    const month2 = req.query.month2 || thisMonth;

    const getByCategory = (month) => {
      const rows = db.prepare(
        "SELECT category, SUM(amount) as total FROM transactions WHERE type='Out' AND date LIKE ? GROUP BY category"
      ).all(`${month}%`);
      const map = {};
      for (const r of rows) map[r.category] = r.total;
      return map;
    };

    const d1 = getByCategory(month1);
    const d2 = getByCategory(month2);
    const allCats = [...new Set([...Object.keys(d1), ...Object.keys(d2)])];

    const comparison = allCats.map(cat => ({
      category: cat,
      [month1]: d1[cat] || 0,
      [month2]: d2[cat] || 0,
      diff: (d2[cat] || 0) - (d1[cat] || 0),
      diffPct: d1[cat] ? Math.round(((d2[cat] || 0) - d1[cat]) / d1[cat] * 100) : null
    }));
    const total1 = Object.values(d1).reduce((s, v) => s + v, 0);
    const total2 = Object.values(d2).reduce((s, v) => s + v, 0);
    res.json({ month1, month2, comparison, total1, total2, totalDiff: total2 - total1 });
  } catch (e) { res.status(500).json({ error: e.message }); }
});

// ============================================================
// GET /api/investments/pl — portfolio + P&L calculation
// ============================================================
app.get('/api/investments/pl', (req, res) => {
  try {
    const rows = db.prepare('SELECT * FROM investments').all();
    let totalCost = 0, totalValue = 0;
    const portfolio = rows.map(inv => {
      const costBasis    = inv.cost_basis || 0;
      const currentValue = inv.current_price ? inv.current_price * (inv.qty || 1) : costBasis;
      const pl           = currentValue - costBasis;
      const plPct        = costBasis > 0 ? Math.round(pl / costBasis * 100 * 10) / 10 : 0;
      totalCost  += costBasis;
      totalValue += currentValue;
      return {
        platform: inv.platform, ticker: inv.ticker, type: inv.type,
        qty: inv.qty, avgBuy: inv.avg_buy, currentPrice: inv.current_price,
        costBasis, currentValue: Math.round(currentValue),
        pl: Math.round(pl), plPct,
        currency: inv.currency, lastUpdate: inv.last_update, notes: inv.notes
      };
    });
    res.json({
      portfolio,
      totalCostBasis: Math.round(totalCost),
      totalCurrentValue: Math.round(totalValue),
      totalPL: Math.round(totalValue - totalCost),
      totalPLPct: totalCost > 0 ? Math.round((totalValue - totalCost) / totalCost * 100 * 10) / 10 : 0
    });
  } catch (e) { res.status(500).json({ error: e.message }); }
});

// ============================================================
// Health check
// ============================================================
app.get('/api/health', (req, res) => {
  const trxCount = db.prepare('SELECT COUNT(*) as count FROM transactions').get();
  res.json({ status: 'ok', transactions: trxCount.count, timestamp: new Date().toISOString() });
});

// ============================================================
// START
// ============================================================
app.listen(PORT, '0.0.0.0', () => {
  console.log(`\n🚀 Finance API running at http://0.0.0.0:${PORT}`);
  console.log(`   Dashboard : http://localhost:${PORT}`);
  console.log(`   API data  : http://localhost:${PORT}/api/data`);
  console.log(`   Health    : http://localhost:${PORT}/api/health\n`);
});
