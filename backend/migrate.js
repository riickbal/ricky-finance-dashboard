// ============================================================
// migrate.js — One-time import dari data.js ke SQLite
// Jalanin sekali: node migrate.js
// ============================================================

const { DatabaseSync } = require('node:sqlite');
const fs = require('fs');
const path = require('path');

// Load schema
const db = new DatabaseSync('finance.db');
const schema = fs.readFileSync(path.join(__dirname, 'schema.sql'), 'utf8');
db.exec(schema);

// ============================================================
// PASTE DATA DARI data.js DI SINI (as plain JS object)
// ============================================================
const DATA = {
  fxRate: 17950,
  lastUpdated: '2026-06-25',
  banks: [
    { name:'Blu By BCA', nick:'BLU 904', cat:'Digital Bank', type:'Tabungan (Digital)', balance:1355000.61, updated:'2026-06-25', acct:'****1904' },
    { name:'BCA', nick:'BCA 062', cat:'Bank', type:'Tabungan', balance:790729.14, updated:'2026-06-26', acct:'****5062' },
    { name:'BCA', nick:'BCA 968', cat:'Bank', type:'Tabungan', balance:3350000.43, updated:'2026-06-27', acct:'****7968' },
    { name:'Permata', nick:'Permata 829', cat:'Bank', type:'Payroll/Giro', balance:15405871.52, updated:'2026-06-27', acct:'****4829' },
    { name:'Permata', nick:'Permata 734', cat:'Bank', type:'Tabungan', balance:7414879, updated:'2026-06-25', acct:'****3734', notes:'Rekening KPR — auto-debit KPR Rp7,400,000 tiap tgl 7' },
    { name:'CIMB Niaga', nick:'CIMB 200', cat:'Bank', type:'Tabungan', balance:50000, updated:'2026-06-25', acct:'****4200' }
  ],
  creditCards: [
    { name:'CC CIMB', issuer:'CIMB Niaga Syariah', limit:59200000, outstanding:16638270.33, dueDate:'', notes:'Refund raket padel Rp3,098,486 sudah balik (25 Jun).' },
    { name:'CC Permata', issuer:'Permata', limit:20500000, outstanding:15466500, dueDate:'', notes:'Acct ****9447. Bayar 5jt tgl 27 Jun.' }
  ],
  loans: [
    { type:'KPR', lender:'Permata', remaining:1128658676, monthly:7400000, rate:0, tenor:0, notes:'Auto-debit dari Permata 734 tiap tgl 7' },
    { type:'KTA', lender:'CIMB Niaga (Xtra Dana)', remaining:47962217.23, monthly:2637444, rate:0, tenor:0 }
  ],
  investments: [
    { platform:'Binance', ticker:'', type:'Crypto', qty:0, avgBuy:0, currency:'USD', costBasis:0, currentPrice:0 },
    { platform:'Binance', ticker:'', type:'Crypto', qty:0, avgBuy:0, currency:'USD', costBasis:0, currentPrice:0 },
    { platform:'Indodax', ticker:'', type:'Crypto', qty:0, avgBuy:0, currency:'IDR', costBasis:0, currentPrice:0 },
    { platform:'Pluang', ticker:'VOO', type:'ETF (US Stock)', qty:0, avgBuy:0, currency:'USD', costBasis:0, currentPrice:0, notes:'CLOSED 2026-06-24.' },
    { platform:'Stockbit', ticker:'BBRI', type:'IDX Stocks', qty:3200, avgBuy:3065.84, currency:'IDR', costBasis:9810694, currentPrice:2810, platformCash:189306, lastUpdate:'2026-06-25' }
  ],
  fixedAssets: [
    { id:'fa1', name:'Mac Mini M4', category:'Electronics', purchaseDate:'2026-06-24', cost:13116500, usefulLifeMonths:48, transactionRef:'t32', notes:'Monthly depreciation: Rp273,260.' }
  ],
  receivables: [
    { id:'rcv1', name:'Satrio', amount:50000, date:'2026-06-26', dueDate:'', notes:'Pinjaman tunai', status:'outstanding' }
  ],
  budgets: {
    'Kebutuhan Dasar Anak': 1700000,
    'Mainan & Edukasi Anak': 200000,
    'Meals': 1000000,
    'Listrik': 1000000,
    'Wifi & Internet': 350000,
    'Transportation': 2800000,
    'Service Vehicle': 500000,
    'Phone Credit': 200000,
    'Wellness (Hobbies & Travel)': 200000,
    'Apps & Subscriptions': 0,
    'Electronics & Accessories': 0,
    'Marketplace / Other': 300000,
    'Interest Expense - KTA': 0,
    'Interest Expense - KPR': 0,
    'Biaya Admin/Fee': 100000,
    'Lain-lain / Belum Jelas': 153000
  },
  income: { salary: 20685871, kprMonthly: 7400000 },
  transactions: [
    {id:'t1',date:'2026-06-20',type:'Transfer',category:'Transfer Internal',account:'Permata -> BCA 730',amount:500000,desc:'Transfer internal Permata ke BCA 7305025062'},
    {id:'t2',date:'2026-06-20',type:'Out',category:'Transportation',account:'CC CIMB',amount:272200,desc:'SPBU 34.158.04 KSO Curug, Tangerang'},
    {id:'t3',date:'2026-06-20',type:'Out',category:'Wellness (Hobbies & Travel)',account:'BCA 730',amount:10000,desc:'QR payment - Padel Geh'},
    {id:'t4',date:'2026-06-20',type:'In',category:'Income - Other',account:'BCA 730',amount:70000,desc:'Transfer masuk dari Lia Uzliawati SE'},
    {id:'t5',date:'2026-06-20',type:'Out',category:'Lain-lain / Belum Jelas',account:'BCA 730',amount:10000,desc:'QR payment - VM Yanmar'},
    {id:'t6',date:'2026-06-20',type:'Out',category:'Transportation',account:'BCA 730',amount:103075,desc:'Top-up Flazz BCA'},
    {id:'t7',date:'2026-06-20',type:'Out',category:'Lain-lain / Belum Jelas',account:'CC CIMB',amount:10000,desc:'QR payment, merchant tidak disebutkan'},
    {id:'t8',date:'2026-06-21',type:'Out',category:'Transportation',account:'BCA 730',amount:50000,desc:'Top-up Flazz BCA'},
    {id:'t9',date:'2026-06-21',type:'Out',category:'Transportation',account:'BCA 730',amount:20480,desc:'SPBU 34.15 - isi bensin motor'},
    {id:'t10',date:'2026-06-21',type:'Out',category:'Meals',account:'BCA 730',amount:26000,desc:'Kabita Ane - beli jus'},
    {id:'t11',date:'2026-06-21',type:'Out',category:'Service Vehicle',account:'BCA 730',amount:247500,desc:'T3 MOTOR - servis motor'},
    {id:'t12',date:'2026-06-21',type:'Out',category:'Meals',account:'BCA 730',amount:12100,desc:'ALFAMART R'},
    {id:'t13',date:'2026-06-21',type:'Transfer',category:'Transfer Internal',account:'Permata -> BCA 730',amount:1000000,desc:'Transfer internal Permata Payroll ke BCA 7305025062'},
    {id:'t14',date:'2026-06-21',type:'Out',category:'Transportation',account:'BCA 730',amount:222360,desc:'GoPay Later - GoRide'},
    {id:'t15',date:'2026-06-21',type:'Out',category:'Meals',account:'BCA 730',amount:294882,desc:'GoPay Later - GoFood'},
    {id:'t16',date:'2026-06-21',type:'Out',category:'Meals',account:'BCA 730',amount:50000,desc:'QRIS - makan malam (baso)'},
    {id:'t17',date:'2026-06-21',type:'Out',category:'Service Vehicle',account:'BCA 730',amount:114700,desc:'Gear Girbox Gigi Speedometer'},
    {id:'t18',date:'2026-06-21',type:'Out',category:'Marketplace / Other',account:'BCA 730',amount:187091,desc:'GoPay Later - Tokopedia'},
    {id:'t19',date:'2026-06-21',type:'Out',category:'Biaya Admin/Fee',account:'BCA 730',amount:56650,desc:'GoPay Later - biaya admin'},
    {id:'t20',date:'2026-06-21',type:'Out',category:'Wellness (Hobbies & Travel)',account:'BCA 730',amount:30000,desc:'Main padel'},
    {id:'t21',date:'2026-06-22',type:'Out',category:'Meals',account:'BCA 730',amount:25000,desc:'WARUNG NAS'},
    {id:'t22',date:'2026-06-22',type:'Out',category:'Transportation',account:'BCA 730',amount:38783,desc:'Top-up GoPay'},
    {id:'t23',date:'2026-06-22',type:'Out',category:'Meals',account:'BCA 730',amount:13500,desc:'Kebab'},
    {id:'t24',date:'2026-06-23',type:'Out',category:'Meals',account:'BCA 730',amount:59900,desc:'Beli rokok dan minuman'},
    {id:'t25',date:'2026-06-23',type:'Out',category:'Liability Payment - KTA',account:'CIMB 707',amount:2837444,desc:'Auto-debit KTA Xtra Dana'},
    {id:'t26',date:'2026-06-23',type:'Out',category:'Meals',account:'CC CIMB',amount:31000,desc:'Warteg makan'},
    {id:'t27',date:'2026-06-24',type:'In',category:'Income - Other',account:'BCA 730',amount:4822619,desc:'VOO ETF Pluang - withdraw settled'},
    {id:'t28',date:'2026-06-24',type:'Transfer',category:'Transfer Internal',account:'BCA 730 -> Permata 829',amount:4500000,desc:'Intercash BCA ke Permata 829'},
    {id:'t29',date:'2026-06-24',type:'Out',category:'Biaya Admin/Fee',account:'BCA 730',amount:2500,desc:'Admin fee intercash ke Permata 829'},
    {id:'t30',date:'2026-06-24',type:'Out',category:'Liability Payment - CC',account:'Permata 412 (Payroll)',amount:2360448,desc:'Bayar tagihan CC Permata'},
    {id:'t31',date:'2026-06-24',type:'Out',category:'Biaya Admin/Fee',account:'Permata 412 (Payroll)',amount:50000,desc:'Fee/denda bayar CC Permata'},
    {id:'t32',date:'2026-06-24',type:'Out',category:'Fixed Asset Purchase',account:'CC Permata',amount:13116500,desc:'Purchase Mac Mini M4'},
    {id:'t33',date:'2026-06-24',type:'Transfer',category:'Transfer Internal',account:'Permata -> BCA 730',amount:1039552,desc:'Transfer Permata 829 ke BCA'},
    {id:'t34',date:'2026-06-24',type:'Out',category:'Electronics & Accessories',account:'BCA 730',amount:900350,desc:'Kebutuhan support Mac Mini'},
    {id:'t35',date:'2026-06-24',type:'Out',category:'Meals',account:'BCA 730',amount:27000,desc:'Warteg makan'},
    {id:'t36',date:'2026-06-24',type:'Out',category:'Meals',account:'BCA 730',amount:108000,desc:'Kopi'},
    {id:'t37',date:'2026-06-24',type:'In',category:'Income - Other',account:'Permata 412 (Payroll)',amount:20000,desc:'Reimbursement parkir'},
    {id:'t38',date:'2026-06-25',type:'In',category:'Income - Salary',account:'Permata 412 (Payroll)',amount:20685871,desc:'Gaji dari PT Esensi Solusi Buana'},
    {id:'t39',date:'2026-06-25',type:'Transfer',category:'Transfer Internal',account:'Permata 829 -> Permata 734',amount:7400000,desc:'Transfer KPR'},
    {id:'t40',date:'2026-06-25',type:'Transfer',category:'Transfer Internal',account:'Permata 829 -> CIMB 200',amount:697000,desc:'Top-up CIMB 200'},
    {id:'t41',date:'2026-06-25',type:'Out',category:'Liability Payment - CC',account:'CIMB 200',amount:500134,desc:'Bayar cicilan CC CIMB'},
    {id:'t42',date:'2026-06-25',type:'Transfer',category:'Transfer Internal',account:'Permata 829 -> BLU 904',amount:1500000,desc:'Budget padel'},
    {id:'t43',date:'2026-06-25',type:'Transfer',category:'Transfer Internal',account:'Permata 829 -> BCA 730',amount:1750000,desc:'Transfer Permata 829 ke BCA 730'},
    {id:'t44',date:'2026-06-25',type:'Out',category:'Mainan & Edukasi Anak',account:'BCA 730',amount:77510,desc:'Mainan anak'},
    {id:'t45',date:'2026-06-25',type:'Out',category:'Electronics & Accessories',account:'BCA 730',amount:141689,desc:'Kabel Type C & HDMI'},
    {id:'t46',date:'2026-06-25',type:'Out',category:'Kebutuhan Dasar Anak',account:'BCA 730',amount:364671,desc:'Pampers Mamypoko Royalsoft'},
    {id:'t47',date:'2026-06-25',type:'Out',category:'Kebutuhan Dasar Anak',account:'BCA 730',amount:1037276,desc:'Susu Morinaga Chilkid Vanilla'},
    {id:'t48',date:'2026-06-25',type:'Out',category:'Biaya Admin/Fee',account:'BCA 730',amount:1000,desc:'Admin variance belanja 25 Jun'},
    {id:'t49',date:'2026-06-25',type:'Out',category:'Apps & Subscriptions',account:'BCA 730',amount:350000,desc:'Langganan Claude AI'},
    {id:'t50',date:'2026-06-25',type:'Transfer',category:'Transfer Internal',account:'Permata 829 -> BCA 730',amount:2353000,desc:'Transfer Permata 829 ke BCA 730'},
    {id:'t51',date:'2026-06-25',type:'Transfer',category:'Transfer Internal',account:'Permata 829 -> BCA 968',amount:3650000,desc:'Transfer Permata 829 ke BCA 968'},
    {id:'t52',date:'2026-06-25',type:'Out',category:'Listrik',account:'BCA 062',amount:1000000,desc:'Bayar tagihan listrik PLN'},
    {id:'t53',date:'2026-06-25',type:'Out',category:'Biaya Admin/Fee',account:'BCA 062',amount:3000,desc:'Admin bayar listrik PLN'},
    {id:'t54',date:'2026-06-25',type:'Out',category:'Wellness (Hobbies & Travel)',account:'BLU 904',amount:145000,desc:'Padel'},
    {id:'t55',date:'2026-06-25',type:'Out',category:'Lain-lain / Belum Jelas',account:'BCA 062',amount:200600,desc:'Patungan kantor'},
    {id:'t56',date:'2026-06-25',type:'Out',category:'Meals',account:'BCA 062',amount:29000,desc:'Makan warteg'},
    {id:'t57',date:'2026-06-25',type:'Out',category:'Meals',account:'BCA 062',amount:23300,desc:'Pocari Sweat + air mineral + Chacha coklat'},
    {id:'t58',date:'2026-06-26',type:'Out',category:'Phone Credit',account:'BCA 062',amount:102000,desc:'Pulsa XL/AXIS 087774466998'},
    {id:'t59',date:'2026-06-26',type:'Out',category:'Phone Credit',account:'BCA 062',amount:17000,desc:'Pulsa XL/AXIS 087774466998'},
    {id:'t60',date:'2026-06-26',type:'Out',category:'Phone Credit',account:'BCA 062',amount:77000,desc:'Pulsa Telkomsel 081219612822'},
    {id:'t61',date:'2026-06-26',type:'Out',category:'Transportation',account:'BCA 968',amount:150000,desc:'Top-up Flazz'},
    {id:'t62',date:'2026-06-26',type:'Out',category:'Meals',account:'BCA 062',amount:10900,desc:'QRIS JUMPSTART Bank Nobu'},
    {id:'t63',date:'2026-06-26',type:'Out',category:'Meals',account:'BCA 062',amount:9500,desc:'JUMPSTART'},
    {id:'t64',date:'2026-06-26',type:'Out',category:'Meals',account:'BCA 062',amount:20000,desc:'Beli Gabin snack'},
    {id:'t65',date:'2026-06-26',type:'Out',category:'Receivable',account:'BCA 062',amount:50000,desc:'Pinjaman ke Satrio'},
    {id:'t66',date:'2026-06-26',type:'Out',category:'Meals',account:'BCA 062',amount:20000,desc:'Mie Tomat Medan'},
    {id:'t67',date:'2026-06-26',type:'Out',category:'Meals',account:'BCA 062',amount:5000,desc:'Cilor jajanan'},
    {id:'t68',date:'2026-06-26',type:'Out',category:'Groceries',account:'BCA 062',amount:98200,desc:'Biji Kopi Espresso - Tokopedia'},
    {id:'t69',date:'2026-06-27',type:'Out',category:'Transportation',account:'BCA 968',amount:150000,desc:'Bensin'},
    {id:'t70',date:'2026-06-27',type:'Out',category:'Liability Payment - CC',account:'Permata 829',amount:5000000,desc:'Bayar cicilan CC Permata'}
  ]
};

// ============================================================
// MIGRATE
// ============================================================
console.log('🚀 Starting migration...');

// Config
const setConfig = db.prepare('INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)');
setConfig.run('fxRate', String(DATA.fxRate));
setConfig.run('lastUpdated', DATA.lastUpdated);
setConfig.run('salary', String(DATA.income.salary));
setConfig.run('kprMonthly', String(DATA.income.kprMonthly));
console.log('✅ Config migrated');

// Banks
const insertBank = db.prepare(`
  INSERT OR REPLACE INTO banks (nick, name, cat, type, acct, balance, updated, notes)
  VALUES (@nick, @name, @cat, @type, @acct, @balance, @updated, @notes)
`);
for (const b of DATA.banks) insertBank.run({ ...b, notes: b.notes || null });
console.log(`✅ Banks migrated (${DATA.banks.length})`);

// Credit cards
const insertCC = db.prepare(`
  INSERT OR REPLACE INTO credit_cards (name, issuer, limit_amt, outstanding, due_date, notes)
  VALUES (@name, @issuer, @limit_amt, @outstanding, @due_date, @notes)
`);
for (const cc of DATA.creditCards) {
  insertCC.run({ name: cc.name, issuer: cc.issuer, limit_amt: cc.limit, outstanding: cc.outstanding, due_date: cc.dueDate || null, notes: cc.notes || null });
}
console.log(`✅ Credit cards migrated (${DATA.creditCards.length})`);

// Loans
const insertLoan = db.prepare(`
  INSERT OR REPLACE INTO loans (type, lender, remaining, monthly, rate, tenor, notes)
  VALUES (@type, @lender, @remaining, @monthly, @rate, @tenor, @notes)
`);
for (const l of DATA.loans) insertLoan.run({ ...l, notes: l.notes || null });
console.log(`✅ Loans migrated (${DATA.loans.length})`);

// Investments
const insertInv = db.prepare(`
  INSERT OR REPLACE INTO investments (platform, ticker, type, qty, avg_buy, currency, cost_basis, current_price, platform_cash, nbv_override, last_update, notes)
  VALUES (@platform, @ticker, @type, @qty, @avg_buy, @currency, @cost_basis, @current_price, @platform_cash, @nbv_override, @last_update, @notes)
`);
for (const inv of DATA.investments) {
  insertInv.run({
    platform: inv.platform, ticker: inv.ticker || null, type: inv.type,
    qty: inv.qty || 0, avg_buy: inv.avgBuy || 0, currency: inv.currency,
    cost_basis: inv.costBasis || 0, current_price: inv.currentPrice || 0,
    platform_cash: inv.platformCash || 0, nbv_override: inv.nbvOverride || null,
    last_update: inv.lastUpdate || null, notes: inv.notes || null
  });
}
console.log(`✅ Investments migrated (${DATA.investments.length})`);

// Fixed assets
const insertFA = db.prepare(`
  INSERT OR REPLACE INTO fixed_assets (id, name, category, purchase_date, cost, useful_life_months, transaction_ref, notes)
  VALUES (@id, @name, @category, @purchase_date, @cost, @useful_life_months, @transaction_ref, @notes)
`);
for (const fa of DATA.fixedAssets) {
  insertFA.run({ id: fa.id, name: fa.name, category: fa.category, purchase_date: fa.purchaseDate, cost: fa.cost, useful_life_months: fa.usefulLifeMonths, transaction_ref: fa.transactionRef || null, notes: fa.notes || null });
}
console.log(`✅ Fixed assets migrated (${DATA.fixedAssets.length})`);

// Receivables
const insertRcv = db.prepare(`
  INSERT OR REPLACE INTO receivables (id, name, amount, date, due_date, notes, status)
  VALUES (@id, @name, @amount, @date, @due_date, @notes, @status)
`);
for (const r of DATA.receivables) {
  insertRcv.run({ id: r.id, name: r.name, amount: r.amount, date: r.date, due_date: r.dueDate || null, notes: r.notes || null, status: r.status });
}
console.log(`✅ Receivables migrated (${DATA.receivables.length})`);

// Budgets
const insertBudget = db.prepare('INSERT OR REPLACE INTO budgets (category, amount) VALUES (?, ?)');
for (const [cat, amt] of Object.entries(DATA.budgets)) insertBudget.run(cat, amt);
console.log(`✅ Budgets migrated (${Object.keys(DATA.budgets).length})`);

// Transactions
const insertTrx = db.prepare(`
  INSERT OR REPLACE INTO transactions (id, date, type, category, account, amount, desc)
  VALUES ($id, $date, $type, $category, $account, $amount, $desc)
`);
db.exec('BEGIN');
for (const t of DATA.transactions) {
  insertTrx.run({ $id: t.id, $date: t.date, $type: t.type, $category: t.category, $account: t.account, $amount: t.amount, $desc: t.desc || null });
}
db.exec('COMMIT');
console.log(`✅ Transactions migrated (${DATA.transactions.length})`);

console.log('\n🎉 Migration complete! Database: finance.db');
db.close();
