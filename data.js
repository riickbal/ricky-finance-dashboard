// ============================================================
// RICKY FINANCE DASHBOARD — Data File
// Edit this file (or let Claude edit it) then push to GitHub
// Last updated: 2026-06-25
// ============================================================

window.DASHBOARD_DATA = {
  fxRate: 17950,
  lastUpdated: '2026-06-25',
  banks: [
    { name:'Blu By BCA', nick:'BLU 904', cat:'Digital Bank', type:'Tabungan (Digital)', balance:1500000.61, updated:'2026-06-25', acct:'****1904' },
    { name:'BCA', nick:'BCA 062', cat:'Bank', type:'Tabungan', balance:1453229.14, updated:'2026-06-25', acct:'****5062' },
    { name:'BCA', nick:'BCA 968', cat:'Bank', type:'Tabungan', balance:3650000.43, updated:'2026-06-25', acct:'****7968' },
    { name:'Permata', nick:'Permata 829', cat:'Bank', type:'Payroll/Giro', balance:20405871.52, updated:'2026-06-25', acct:'****4829' },
    { name:'Permata', nick:'Permata 734', cat:'Bank', type:'Tabungan', balance:7414879, updated:'2026-06-25', acct:'****3734', notes:'Rekening KPR — auto-debit KPR Rp7,400,000 tiap tgl 7' },
    { name:'CIMB Niaga', nick:'CIMB 200', cat:'Bank', type:'Tabungan', balance:50000, updated:'2026-06-25', acct:'****4200' }
  ],
  creditCards: [
    { name:'MC Plat. Syariah Bundling', issuer:'CIMB Niaga Syariah', limit:59200000, outstanding:16638270.33, dueDate:'', notes:'Refund raket padel Rp3,098,486 sudah balik (25 Jun). Bayar cicilan Rp500,134 (25 Jun). Available limit Rp42,561,729.67.' },
    { name:'Permata Cashback Card', issuer:'Permata', limit:20500000, outstanding:20466500, dueDate:'', notes:'Acct ****9447. Limit sementara Rp20,500,000 s/d 8 Agu 2026 (normal Rp10,000,000). Outstanding prev 9,760,477.93 + Mac Mini 13,116,500 - bayar 2,360,448 = ~20,466,500. Available limit: Rp33,500.' }
  ],
  loans: [
    { type:'KPR', lender:'Permata', remaining:1128658676, monthly:7400000, rate:0, tenor:0, notes:'Auto-debit dari Permata 734 tiap tgl 7' },
    { type:'KTA', lender:'CIMB Niaga (Xtra Dana)', remaining:47962217.23, monthly:2637444, rate:0, tenor:0 }
  ],
  investments: [
    { platform:'Binance', ticker:'', type:'Crypto', qty:0, avgBuy:0, currency:'USD', costBasis:0, currentPrice:0 },
    { platform:'Binance', ticker:'', type:'Crypto', qty:0, avgBuy:0, currency:'USD', costBasis:0, currentPrice:0 },
    { platform:'Indodax', ticker:'', type:'Crypto', qty:0, avgBuy:0, currency:'IDR', costBasis:0, currentPrice:0 },
    { platform:'Pluang', ticker:'VOO', type:'ETF (US Stock)', qty:0, avgBuy:0, currency:'USD', costBasis:0, currentPrice:0, notes:'CLOSED 2026-06-24. Withdraw settled BCA 730. Realized loss Rp177,381 (modal 5jt, settled 4,822,619).' },
    { platform:'Stockbit', ticker:'BBRI', type:'Saham IDX', qty:3200, avgBuy:3065.84, currency:'IDR', costBasis:9810694, currentPrice:2810, platformCash:189306, lastUpdate:'2026-06-25', notes:'32 lot BBRI @ avg 3,065.84. Cash idle di Stockbit: Rp189,306. Total saldo Stockbit (saham + cash) = NBV + 189,306.' }
  ],
  transactions: [
    // === BEGIN BALANCE ===
    // (Saldo awal sistem — sebelum trx pertama Jun 2026 dicatat)
    // BLU ****1904   : Rp0.61
    // BCA ****5062   : ~Rp0 (diisi dari transfer masuk)
    // BCA ****7968   : Rp0.43
    // Permata ****4829: ~Rp0 (diisi dari gaji)
    // CIMB ****4200  : ~Rp0
    // CC CIMB        : outstanding awal ~Rp23,635,820.84 (sebelum Mei-Jun)
    // CC Permata     : outstanding awal ~Rp9,760,477.93

    // --- Jun 20 ---
    {id:'t1',date:'2026-06-20',type:'Transfer',category:'Transfer Internal',account:'Permata -> BCA 730',amount:500000,desc:'Transfer internal Permata ke BCA 7305025062'},
    {id:'t2',date:'2026-06-20',type:'Out',category:'Transportation',account:'CIMB Credit Card (MC Plat Syariah)',amount:272200,desc:'SPBU 34.158.04 KSO Curug, Tangerang'},
    {id:'t3',date:'2026-06-20',type:'Out',category:'Wellness (Hobbies & Travel)',account:'BCA 730',amount:10000,desc:'QR payment - Padel Geh'},
    {id:'t4',date:'2026-06-20',type:'In',category:'Income - Other',account:'BCA 730',amount:70000,desc:'Transfer masuk dari Lia Uzliawati SE'},
    {id:'t5',date:'2026-06-20',type:'Out',category:'Lain-lain / Belum Jelas',account:'BCA 730',amount:10000,desc:'QR payment - VM Yanmar'},
    {id:'t6',date:'2026-06-20',type:'Out',category:'Transportation',account:'BCA 730',amount:103075,desc:'Top-up Flazz BCA'},
    {id:'t7',date:'2026-06-20',type:'Out',category:'Lain-lain / Belum Jelas',account:'CIMB Credit Card (MC Plat Syariah)',amount:10000,desc:'QR payment, merchant tidak disebutkan'},
    // --- Jun 21 ---
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
    // --- Jun 22 ---
    {id:'t21',date:'2026-06-22',type:'Out',category:'Meals',account:'BCA 730',amount:25000,desc:'WARUNG NAS'},
    {id:'t22',date:'2026-06-22',type:'Out',category:'Transportation',account:'BCA 730',amount:38783,desc:'Top-up GoPay'},
    {id:'t23',date:'2026-06-22',type:'Out',category:'Meals',account:'BCA 730',amount:13500,desc:'Kebab (ditagih temen)'},
    // --- Jun 23 ---
    {id:'t24',date:'2026-06-23',type:'Out',category:'Meals',account:'BCA 730',amount:59900,desc:'Beli rokok dan minuman'},
    {id:'t25',date:'2026-06-23',type:'Out',category:'Pembayaran Utang/Cicilan',account:'CIMB 707',amount:2837444,desc:'Auto-debit KTA Xtra Dana (cicilan Rp2,637,444 + late charge Rp200,000)'},
    {id:'t26',date:'2026-06-23',type:'Out',category:'Meals',account:'CIMB Credit Card (MC Plat Syariah)',amount:31000,desc:'Warteg makan'},
    // --- Jun 24 ---
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
    // --- Jun 25 ---
    {id:'t38',date:'2026-06-25',type:'In',category:'Income - Salary',account:'Permata 412 (Payroll)',amount:20685871,desc:'Gaji dari PT Esensi Solusi Buana'},
    {id:'t39',date:'2026-06-25',type:'Transfer',category:'Transfer Internal',account:'Permata 829 -> Permata 734',amount:7400000,desc:'Transfer KPR — ke Permata 9839913734 (auto-debit KPR tgl 7 tiap bulan)'},
    {id:'t40',date:'2026-06-25',type:'Transfer',category:'Transfer Internal',account:'Permata 829 -> CIMB 200',amount:697000,desc:'Top-up CIMB 200 untuk cover bayar cicilan CC CIMB'},
    {id:'t41',date:'2026-06-25',type:'Out',category:'Pembayaran Utang/Cicilan',account:'CIMB 200',amount:500134,desc:'Bayar cicilan CC CIMB Plat Syariah'},
    {id:'t42',date:'2026-06-25',type:'Transfer',category:'Transfer Internal',account:'Permata 829 -> BLU 904',amount:1500000,desc:'Budget padel — transfer ke BLU ****1904 (budget only, belum realisasi padel)'},
    {id:'t43',date:'2026-06-25',type:'Transfer',category:'Transfer Internal',account:'Permata 829 -> BCA 730',amount:1750000,desc:'Transfer Permata 829 ke BCA 7305025062'},
    {id:'t44',date:'2026-06-25',type:'Out',category:'Daughter Needs',account:'BCA 730',amount:77510,desc:'Mainan anak'},
    {id:'t45',date:'2026-06-25',type:'Out',category:'Shopping/Belanja Online',account:'BCA 730',amount:141689,desc:'Kabel Type C & HDMI (kebutuhan Mac Mini)'},
    {id:'t46',date:'2026-06-25',type:'Out',category:'Daughter Needs',account:'BCA 730',amount:364671,desc:'Pampers Mamypoko Royalsoft 3 bundle isi 52 ukuran L'},
    {id:'t47',date:'2026-06-25',type:'Out',category:'Daughter Needs',account:'BCA 730',amount:1037276,desc:'Susu Morinaga Chilkid Vanilla 800gr 1-3 Tahun 4 pcs'},
    {id:'t48',date:'2026-06-25',type:'Out',category:'Biaya Admin/Fee',account:'BCA 730',amount:1000,desc:'Admin variance belanja 25 Jun'},
    {id:'t49',date:'2026-06-25',type:'Out',category:'Subscription',account:'BCA 730',amount:350000,desc:'⚠️ Langganan Claude AI (29 Jun–28 Jul) — RECURRING tiap tgl 29 via BCA 730'},
    {id:'t50',date:'2026-06-25',type:'Transfer',category:'Transfer Internal',account:'Permata 829 -> BCA 730',amount:2353000,desc:'Transfer Permata 829 ke BCA 7305025062'},
    {id:'t51',date:'2026-06-25',type:'Transfer',category:'Transfer Internal',account:'Permata 829 -> BCA 968',amount:3650000,desc:'Transfer Permata 829 ke BCA ****7968 (BCA 968)'},
    {id:'t52',date:'2026-06-25',type:'Out',category:'Listrik',account:'BCA 062',amount:1000000,desc:'Bayar tagihan listrik PLN'},
    {id:'t53',date:'2026-06-25',type:'Out',category:'Biaya Admin/Fee',account:'BCA 062',amount:3000,desc:'Admin bayar listrik PLN'},
  ],
  budgets: {
    'Daughter Needs':0,
    'Listrik':1000000,
    'Wifi & Internet':350000,
    'Utilities & Household':0,
    'Transportation':2800000,
    'Service Vehicle':500000,
    'Meals':1000000,
    'Phone Credit':200000,
    'Subscription':0,
    'Wellness (Hobbies & Travel)':200000,
    'Shopping/Belanja Online':300000,
    'Pembayaran Utang/Cicilan':3000000,
    'Biaya Admin/Fee':100000,
    'Lain-lain / Belum Jelas':153000
  },
  income: { salary:20685871, kprMonthly:7400000 }
}
