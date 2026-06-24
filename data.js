// ============================================================
// RICKY FINANCE DASHBOARD — Data File
// Edit this file (or let Claude edit it) then push to GitHub
// Last updated: 2026-06-24
// ============================================================

window.DASHBOARD_DATA = {
  fxRate: 17819,
  lastUpdated: '2026-06-24',
  banks: [
    { name:'Blu By BCA', nick:'blu by BCA', cat:'Digital Bank', type:'Tabungan (Digital)', balance:0.61, updated:'2026-06-20', acct:'****1904' },
    { name:'BCA', nick:'m-Info Acct 1 (730)', cat:'Bank', type:'Tabungan', balance:325375.14, updated:'2026-06-24', acct:'****5062' },
    { name:'BCA', nick:'m-Info Acct 2 (245)', cat:'Bank', type:'Tabungan', balance:0.43, updated:'2026-06-20', acct:'****7968' },
    { name:'Permata', nick:'Payroll Account', cat:'Bank', type:'Payroll/Giro', balance:17070000.52, updated:'2026-06-24', acct:'****4829' },
    { name:'CIMB Niaga', nick:'Auto-debit KTA', cat:'Bank', type:'Tabungan', balance:-146866, updated:'2026-06-23', acct:'****4200' }
  ],
  creditCards: [
    { name:'MC Plat. Syariah Bundling', issuer:'CIMB Niaga Syariah', limit:59200000, outstanding:20236890.33, dueDate:'', notes:'Rp3,098,486 PENDING REFUND (raket padel Tokopedia dibatalkan). Available limit belum dipulihkan.' },
    { name:'Permata Cashback Card', issuer:'Permata', limit:20500000, outstanding:20466500, dueDate:'', notes:'Acct ****9447. Limit sementara Rp20,500,000 s/d 8 Agu 2026 (normal Rp10,000,000). Outstanding prev 9,760,477.93 + Mac Mini 13,116,500 - bayar 2,360,448 = ~20,466,500. Available limit: Rp33,500.' }
  ],
  loans: [
    { type:'KPR', lender:'Permata', remaining:1128658676, monthly:0, rate:0, tenor:0 },
    { type:'KTA', lender:'CIMB Niaga (Xtra Dana)', remaining:47962217.23, monthly:2637444, rate:0, tenor:0 }
  ],
  investments: [
    { platform:'Binance', ticker:'', type:'Crypto', qty:0, avgBuy:0, currency:'USD', costBasis:0, currentPrice:0 },
    { platform:'Binance', ticker:'', type:'Crypto', qty:0, avgBuy:0, currency:'USD', costBasis:0, currentPrice:0 },
    { platform:'Indodax', ticker:'', type:'Crypto', qty:0, avgBuy:0, currency:'IDR', costBasis:0, currentPrice:0 },
    { platform:'Pluang', ticker:'VOO', type:'ETF (US Stock)', qty:0, avgBuy:0, currency:'USD', costBasis:0, currentPrice:0, notes:'CLOSED 2026-06-24. Withdraw settled BCA 730. Realized loss Rp177,381 (modal 5jt, settled 4,822,619).' },
    { platform:'Stockbit', ticker:'BBRI', type:'Saham IDX', qty:0, avgBuy:0, currency:'IDR', costBasis:10000000, currentPrice:0, nbvOverride:9376000, lastUpdate:'2026-06-20' }
  ],
  transactions: [
    {id:'t1',date:'2026-06-20',type:'Transfer',category:'Transfer Internal',account:'Permata -> BCA 730',amount:500000,desc:'Transfer internal Permata ke BCA 7305025062'},
    {id:'t2',date:'2026-06-20',type:'Out',category:'Transportation',account:'CIMB Credit Card (MC Plat Syariah)',amount:272200,desc:'SPBU 34.158.04 KSO Curug, Tangerang'},
    {id:'t3',date:'2026-06-20',type:'Out',category:'Wellness (Hobbies & Travel)',account:'BCA 730',amount:10000,desc:'QR payment - Padel Geh'},
    {id:'t4',date:'2026-06-20',type:'In',category:'Income - Other',account:'BCA 730',amount:70000,desc:'Transfer masuk dari Lia Uzliawati SE'},
    {id:'t5',date:'2026-06-20',type:'Out',category:'Lain-lain / Belum Jelas',account:'BCA 730',amount:10000,desc:'QR payment - VM Yanmar'},
    {id:'t6',date:'2026-06-20',type:'Out',category:'Transportation',account:'BCA 730',amount:103075,desc:'Top-up Flazz BCA'},
    {id:'t7',date:'2026-06-20',type:'Out',category:'Lain-lain / Belum Jelas',account:'CIMB Credit Card (MC Plat Syariah)',amount:10000,desc:'QR payment, merchant tidak disebutkan'},
    {id:'t8',date:'2026-06-21',type:'Out',category:'Transportation',account:'BCA 730',amount:50000,desc:'Top-up Flazz BCA, Ref 178200602896'},
    {id:'t9',date:'2026-06-21',type:'Out',category:'Transportation',account:'BCA 730',amount:20480,desc:'SPBU 34.15 - isi bensin motor'},
    {id:'t10',date:'2026-06-21',type:'Out',category:'Meals',account:'BCA 730',amount:26000,desc:'Kabita Ane - beli jus'},
    {id:'t11',date:'2026-06-21',type:'Out',category:'Service Vehicle',account:'BCA 730',amount:247500,desc:'T3 MOTOR - servis motor'},
    {id:'t12',date:'2026-06-21',type:'Out',category:'Meals',account:'BCA 730',amount:12100,desc:'ALFAMART R'},
    {id:'t13',date:'2026-06-21',type:'Transfer',category:'Transfer Internal',account:'Permata -> BCA 730',amount:1000000,desc:'Transfer internal Permata Payroll ke BCA 7305025062'},
    {id:'t14',date:'2026-06-21',type:'Out',category:'Transportation',account:'BCA 730',amount:222360,desc:'GoPay Later - GoRide (12 trip, 24 Mei-17 Jun)'},
    {id:'t15',date:'2026-06-21',type:'Out',category:'Meals',account:'BCA 730',amount:294882,desc:'GoPay Later - GoFood (5 order, 19 Mei-17 Jun)'},
    {id:'t16',date:'2026-06-21',type:'Out',category:'Meals',account:'BCA 730',amount:50000,desc:'QRIS - makan malam (baso)'},
    {id:'t17',date:'2026-06-21',type:'Out',category:'Service Vehicle',account:'BCA 730',amount:114700,desc:'Gear Girbox Gigi Speedometer - MoonLight_SparepartMotorOri'},
    {id:'t18',date:'2026-06-21',type:'Out',category:'Shopping/Belanja Online',account:'BCA 730',amount:187091,desc:'GoPay Later - Tokopedia (3 transaksi, 21 Mei-19 Jun)'},
    {id:'t19',date:'2026-06-21',type:'Out',category:'Biaya Admin/Fee',account:'BCA 730',amount:56650,desc:'GoPay Later - biaya admin/proses pelunasan'},
    {id:'t20',date:'2026-06-21',type:'Out',category:'Wellness (Hobbies & Travel)',account:'BCA 730',amount:30000,desc:'Main padel - transfer ke Agung Aditya Saputra'},
    {id:'t21',date:'2026-06-22',type:'Out',category:'Meals',account:'BCA 730',amount:25000,desc:'WARUNG NAS'},
    {id:'t22',date:'2026-06-22',type:'Out',category:'Transportation',account:'BCA 730',amount:38783,desc:'Top-up GoPay'},
    {id:'t23',date:'2026-06-22',type:'Out',category:'Meals',account:'BCA 730',amount:13500,desc:'Kebab (ditagih temen)'},
    {id:'t24',date:'2026-06-23',type:'Out',category:'Meals',account:'BCA 730',amount:59900,desc:'Beli rokok dan minuman'},
    {id:'t25',date:'2026-06-23',type:'Out',category:'Pembayaran Utang/Cicilan',account:'CIMB 707',amount:2837444,desc:'Auto-debit KTA Xtra Dana (cicilan Rp2,637,444 + late charge Rp200,000)'},
    {id:'t26',date:'2026-06-23',type:'Out',category:'Meals',account:'CIMB Credit Card (MC Plat Syariah)',amount:31000,desc:'Warteg makan'},
    {id:'t27',date:'2026-06-24',type:'In',category:'Income - Other',account:'BCA 730',amount:4822619,desc:'VOO ETF Pluang - withdraw settled ke BCA 7305025062. Selling price 4,827,614 → net settled 4,822,619 (forex gap 4,995). Realized loss vs modal Rp177,381.'},
    {id:'t28',date:'2026-06-24',type:'Transfer',category:'Transfer Internal',account:'BCA 730 -> Permata 829',amount:4500000,desc:'Intercash BCA 7305025062 ke Permata 829 (via intercash service)'},
    {id:'t29',date:'2026-06-24',type:'Out',category:'Biaya Admin/Fee',account:'BCA 730',amount:2500,desc:'Admin fee intercash ke Permata 829'},
    {id:'t30',date:'2026-06-24',type:'Out',category:'Pembayaran Utang/Cicilan',account:'Permata 412 (Payroll)',amount:2360448,desc:'Bayar tagihan CC Permata Cashback Card (****9447)'},
    {id:'t31',date:'2026-06-24',type:'Out',category:'Biaya Admin/Fee',account:'Permata 412 (Payroll)',amount:50000,desc:'Fee/denda bayar CC Permata'},
    {id:'t32',date:'2026-06-24',type:'Out',category:'Shopping/Belanja Online',account:'Permata Cashback Card',amount:13116500,desc:'Purchase Mac Mini M4'},
    {id:'t33',date:'2026-06-24',type:'Transfer',category:'Transfer Internal',account:'Permata -> BCA 730',amount:1039552,desc:'Transfer Permata 829 ke BCA 7305025062'},
    {id:'t34',date:'2026-06-24',type:'Out',category:'Shopping/Belanja Online',account:'BCA 730',amount:900350,desc:'Kebutuhan support Mac Mini - Keyboard, HDMI, KVM, stop kontak ampere'},
    {id:'t35',date:'2026-06-24',type:'Out',category:'Meals',account:'BCA 730',amount:27000,desc:'Warteg makan'},
    {id:'t36',date:'2026-06-24',type:'Out',category:'Meals',account:'BCA 730',amount:108000,desc:'Kopi'},
    {id:'t37',date:'2026-06-24',type:'In',category:'Income - Other',account:'Permata 412 (Payroll)',amount:20000,desc:'Reimbursement parkir'},
  ],
  budgets: {
    'Daughter Needs':0,'Utilities & Household':0,'Transportation':700000,
    'Service Vehicle':200000,'Meals':600000,'Phone Credit':0,'Subscription':0,
    'Wellness (Hobbies & Travel)':200000,'Shopping/Belanja Online':300000,
    'Pembayaran Utang/Cicilan':3000000,'Biaya Admin/Fee':100000,'Lain-lain / Belum Jelas':100000
  },
  income: { salary:0, kprMonthly:0 }
}
