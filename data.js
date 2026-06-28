// data.js — Auto-synced from Finance API
// Last updated: 2026-06-28 20:53:17
// DO NOT EDIT MANUALLY — managed by Edith

const FINANCE_DATA = {
  "fxRate": 17950,
  "lastUpdated": "2026-06-25",
  "banks": [
    {
      "name": "Blu By BCA",
      "nick": "BLU 904",
      "cat": "Digital Bank",
      "type": "Tabungan (Digital)",
      "acct": "****1904",
      "balance": 1355000.61,
      "updated": "2026-06-25",
      "notes": null
    },
    {
      "name": "BCA",
      "nick": "BCA 062",
      "cat": "Bank",
      "type": "Tabungan",
      "acct": "****5062",
      "balance": 790729.14,
      "updated": "2026-06-26",
      "notes": null
    },
    {
      "name": "BCA",
      "nick": "BCA 968",
      "cat": "Bank",
      "type": "Tabungan",
      "acct": "****7968",
      "balance": 3350000.43,
      "updated": "2026-06-27",
      "notes": null
    },
    {
      "name": "Permata",
      "nick": "Permata 829",
      "cat": "Bank",
      "type": "Payroll/Giro",
      "acct": "****4829",
      "balance": 15405871.52,
      "updated": "2026-06-27",
      "notes": null
    },
    {
      "name": "Permata",
      "nick": "Permata 734",
      "cat": "Bank",
      "type": "Tabungan",
      "acct": "****3734",
      "balance": 7414879,
      "updated": "2026-06-25",
      "notes": "Rekening KPR — auto-debit KPR Rp7,400,000 tiap tgl 7"
    },
    {
      "name": "CIMB Niaga",
      "nick": "CIMB 200",
      "cat": "Bank",
      "type": "Tabungan",
      "acct": "****4200",
      "balance": 50000,
      "updated": "2026-06-25",
      "notes": null
    },
    {
      "name": "Permata",
      "nick": "Permata 598",
      "cat": "Bank",
      "type": "Tabungan",
      "acct": "4144397598",
      "balance": 1808885,
      "updated": "2026-06-28",
      "notes": null
    }
  ],
  "creditCards": [
    {
      "name": "CC CIMB",
      "issuer": "CIMB Niaga Syariah",
      "limit": 59200000,
      "outstanding": 16638270.33,
      "dueDate": null,
      "notes": "Refund raket padel Rp3,098,486 sudah balik (25 Jun)."
    },
    {
      "name": "CC Permata",
      "issuer": "Permata",
      "limit": 20500000,
      "outstanding": 15466500,
      "dueDate": null,
      "notes": "Acct ****9447. Bayar 5jt tgl 27 Jun."
    }
  ],
  "loans": [
    {
      "type": "KPR",
      "lender": "Permata",
      "remaining": 1128658676,
      "monthly": 7400000,
      "rate": 0,
      "tenor": 0,
      "notes": "Auto-debit dari Permata 734 tiap tgl 7"
    },
    {
      "type": "KTA",
      "lender": "CIMB Niaga (Xtra Dana)",
      "remaining": 47962217.23,
      "monthly": 2637444,
      "rate": 0,
      "tenor": 0,
      "notes": null
    }
  ],
  "investments": [
    {
      "platform": "Binance",
      "ticker": null,
      "type": "Crypto",
      "qty": 0,
      "avgBuy": 0,
      "currency": "USD",
      "costBasis": 0,
      "currentPrice": 0,
      "platformCash": 0,
      "nbvOverride": null,
      "lastUpdate": null,
      "notes": null
    },
    {
      "platform": "Binance",
      "ticker": null,
      "type": "Crypto",
      "qty": 0,
      "avgBuy": 0,
      "currency": "USD",
      "costBasis": 0,
      "currentPrice": 0,
      "platformCash": 0,
      "nbvOverride": null,
      "lastUpdate": null,
      "notes": null
    },
    {
      "platform": "Indodax",
      "ticker": null,
      "type": "Crypto",
      "qty": 0,
      "avgBuy": 0,
      "currency": "IDR",
      "costBasis": 0,
      "currentPrice": 0,
      "platformCash": 0,
      "nbvOverride": null,
      "lastUpdate": null,
      "notes": null
    },
    {
      "platform": "Pluang",
      "ticker": "VOO",
      "type": "ETF (US Stock)",
      "qty": 0,
      "avgBuy": 0,
      "currency": "USD",
      "costBasis": 0,
      "currentPrice": 0,
      "platformCash": 0,
      "nbvOverride": null,
      "lastUpdate": null,
      "notes": "CLOSED 2026-06-24."
    },
    {
      "platform": "Stockbit",
      "ticker": "BBRI",
      "type": "IDX Stocks",
      "qty": 3200,
      "avgBuy": 3065.84,
      "currency": "IDR",
      "costBasis": 9810694,
      "currentPrice": 2810,
      "platformCash": 189306,
      "nbvOverride": null,
      "lastUpdate": "2026-06-25",
      "notes": null
    }
  ],
  "fixedAssets": [
    {
      "id": "fa1",
      "name": "Mac Mini M4",
      "category": "Electronics",
      "purchaseDate": "2026-06-24",
      "cost": 13116500,
      "usefulLifeMonths": 48,
      "transactionRef": "t32",
      "notes": "Monthly depreciation: Rp273,260."
    }
  ],
  "receivables": [
    {
      "id": "rcv1",
      "name": "Satrio",
      "amount": 50000,
      "date": "2026-06-26",
      "dueDate": null,
      "notes": "Pinjaman tunai",
      "status": "outstanding",
      "settledOn": null
    }
  ],
  "transactions": [
    {
      "id": "t70",
      "date": "2026-06-27",
      "type": "Out",
      "category": "Liability Payment - CC",
      "account": "Permata 829",
      "amount": 5000000,
      "desc": "Bayar cicilan CC Permata"
    },
    {
      "id": "t69",
      "date": "2026-06-27",
      "type": "Out",
      "category": "Transportation",
      "account": "BCA 968",
      "amount": 150000,
      "desc": "Bensin"
    },
    {
      "id": "t68",
      "date": "2026-06-26",
      "type": "Out",
      "category": "Groceries",
      "account": "BCA 062",
      "amount": 98200,
      "desc": "Biji Kopi Espresso - Tokopedia"
    },
    {
      "id": "t67",
      "date": "2026-06-26",
      "type": "Out",
      "category": "Meals",
      "account": "BCA 062",
      "amount": 5000,
      "desc": "Cilor jajanan"
    },
    {
      "id": "t66",
      "date": "2026-06-26",
      "type": "Out",
      "category": "Meals",
      "account": "BCA 062",
      "amount": 20000,
      "desc": "Mie Tomat Medan"
    },
    {
      "id": "t65",
      "date": "2026-06-26",
      "type": "Out",
      "category": "Receivable",
      "account": "BCA 062",
      "amount": 50000,
      "desc": "Pinjaman ke Satrio"
    },
    {
      "id": "t64",
      "date": "2026-06-26",
      "type": "Out",
      "category": "Meals",
      "account": "BCA 062",
      "amount": 20000,
      "desc": "Beli Gabin snack"
    },
    {
      "id": "t63",
      "date": "2026-06-26",
      "type": "Out",
      "category": "Meals",
      "account": "BCA 062",
      "amount": 9500,
      "desc": "JUMPSTART"
    },
    {
      "id": "t62",
      "date": "2026-06-26",
      "type": "Out",
      "category": "Meals",
      "account": "BCA 062",
      "amount": 10900,
      "desc": "QRIS JUMPSTART Bank Nobu"
    },
    {
      "id": "t61",
      "date": "2026-06-26",
      "type": "Out",
      "category": "Transportation",
      "account": "BCA 968",
      "amount": 150000,
      "desc": "Top-up Flazz"
    },
    {
      "id": "t60",
      "date": "2026-06-26",
      "type": "Out",
      "category": "Phone Credit",
      "account": "BCA 062",
      "amount": 77000,
      "desc": "Pulsa Telkomsel 081219612822"
    },
    {
      "id": "t59",
      "date": "2026-06-26",
      "type": "Out",
      "category": "Phone Credit",
      "account": "BCA 062",
      "amount": 17000,
      "desc": "Pulsa XL/AXIS 087774466998"
    },
    {
      "id": "t58",
      "date": "2026-06-26",
      "type": "Out",
      "category": "Phone Credit",
      "account": "BCA 062",
      "amount": 102000,
      "desc": "Pulsa XL/AXIS 087774466998"
    },
    {
      "id": "t57",
      "date": "2026-06-25",
      "type": "Out",
      "category": "Meals",
      "account": "BCA 062",
      "amount": 23300,
      "desc": "Pocari Sweat + air mineral + Chacha coklat"
    },
    {
      "id": "t56",
      "date": "2026-06-25",
      "type": "Out",
      "category": "Meals",
      "account": "BCA 062",
      "amount": 29000,
      "desc": "Makan warteg"
    },
    {
      "id": "t55",
      "date": "2026-06-25",
      "type": "Out",
      "category": "Lain-lain / Belum Jelas",
      "account": "BCA 062",
      "amount": 200600,
      "desc": "Patungan kantor"
    },
    {
      "id": "t54",
      "date": "2026-06-25",
      "type": "Out",
      "category": "Wellness (Hobbies & Travel)",
      "account": "BLU 904",
      "amount": 145000,
      "desc": "Padel"
    },
    {
      "id": "t53",
      "date": "2026-06-25",
      "type": "Out",
      "category": "Biaya Admin/Fee",
      "account": "BCA 062",
      "amount": 3000,
      "desc": "Admin bayar listrik PLN"
    },
    {
      "id": "t52",
      "date": "2026-06-25",
      "type": "Out",
      "category": "Listrik",
      "account": "BCA 062",
      "amount": 1000000,
      "desc": "Bayar tagihan listrik PLN"
    },
    {
      "id": "t51",
      "date": "2026-06-25",
      "type": "Transfer",
      "category": "Transfer Internal",
      "account": "Permata 829 -> BCA 968",
      "amount": 3650000,
      "desc": "Transfer Permata 829 ke BCA 968"
    },
    {
      "id": "t50",
      "date": "2026-06-25",
      "type": "Transfer",
      "category": "Transfer Internal",
      "account": "Permata 829 -> BCA 730",
      "amount": 2353000,
      "desc": "Transfer Permata 829 ke BCA 730"
    },
    {
      "id": "t49",
      "date": "2026-06-25",
      "type": "Out",
      "category": "Apps & Subscriptions",
      "account": "BCA 730",
      "amount": 350000,
      "desc": "Langganan Claude AI"
    },
    {
      "id": "t48",
      "date": "2026-06-25",
      "type": "Out",
      "category": "Biaya Admin/Fee",
      "account": "BCA 730",
      "amount": 1000,
      "desc": "Admin variance belanja 25 Jun"
    },
    {
      "id": "t47",
      "date": "2026-06-25",
      "type": "Out",
      "category": "Kebutuhan Dasar Anak",
      "account": "BCA 730",
      "amount": 1037276,
      "desc": "Susu Morinaga Chilkid Vanilla"
    },
    {
      "id": "t46",
      "date": "2026-06-25",
      "type": "Out",
      "category": "Kebutuhan Dasar Anak",
      "account": "BCA 730",
      "amount": 364671,
      "desc": "Pampers Mamypoko Royalsoft"
    },
    {
      "id": "t45",
      "date": "2026-06-25",
      "type": "Out",
      "category": "Electronics & Accessories",
      "account": "BCA 730",
      "amount": 141689,
      "desc": "Kabel Type C & HDMI"
    },
    {
      "id": "t44",
      "date": "2026-06-25",
      "type": "Out",
      "category": "Mainan & Edukasi Anak",
      "account": "BCA 730",
      "amount": 77510,
      "desc": "Mainan anak"
    },
    {
      "id": "t43",
      "date": "2026-06-25",
      "type": "Transfer",
      "category": "Transfer Internal",
      "account": "Permata 829 -> BCA 730",
      "amount": 1750000,
      "desc": "Transfer Permata 829 ke BCA 730"
    },
    {
      "id": "t42",
      "date": "2026-06-25",
      "type": "Transfer",
      "category": "Transfer Internal",
      "account": "Permata 829 -> BLU 904",
      "amount": 1500000,
      "desc": "Budget padel"
    },
    {
      "id": "t41",
      "date": "2026-06-25",
      "type": "Out",
      "category": "Liability Payment - CC",
      "account": "CIMB 200",
      "amount": 500134,
      "desc": "Bayar cicilan CC CIMB"
    },
    {
      "id": "t40",
      "date": "2026-06-25",
      "type": "Transfer",
      "category": "Transfer Internal",
      "account": "Permata 829 -> CIMB 200",
      "amount": 697000,
      "desc": "Top-up CIMB 200"
    },
    {
      "id": "t39",
      "date": "2026-06-25",
      "type": "Transfer",
      "category": "Transfer Internal",
      "account": "Permata 829 -> Permata 734",
      "amount": 7400000,
      "desc": "Transfer KPR"
    },
    {
      "id": "t38",
      "date": "2026-06-25",
      "type": "In",
      "category": "Income - Salary",
      "account": "Permata 412 (Payroll)",
      "amount": 20685871,
      "desc": "Gaji dari PT Esensi Solusi Buana"
    },
    {
      "id": "t37",
      "date": "2026-06-24",
      "type": "In",
      "category": "Income - Other",
      "account": "Permata 412 (Payroll)",
      "amount": 20000,
      "desc": "Reimbursement parkir"
    },
    {
      "id": "t36",
      "date": "2026-06-24",
      "type": "Out",
      "category": "Meals",
      "account": "BCA 730",
      "amount": 108000,
      "desc": "Kopi"
    },
    {
      "id": "t35",
      "date": "2026-06-24",
      "type": "Out",
      "category": "Meals",
      "account": "BCA 730",
      "amount": 27000,
      "desc": "Warteg makan"
    },
    {
      "id": "t34",
      "date": "2026-06-24",
      "type": "Out",
      "category": "Electronics & Accessories",
      "account": "BCA 730",
      "amount": 900350,
      "desc": "Kebutuhan support Mac Mini"
    },
    {
      "id": "t33",
      "date": "2026-06-24",
      "type": "Transfer",
      "category": "Transfer Internal",
      "account": "Permata -> BCA 730",
      "amount": 1039552,
      "desc": "Transfer Permata 829 ke BCA"
    },
    {
      "id": "t32",
      "date": "2026-06-24",
      "type": "Out",
      "category": "Fixed Asset Purchase",
      "account": "CC Permata",
      "amount": 13116500,
      "desc": "Purchase Mac Mini M4"
    },
    {
      "id": "t31",
      "date": "2026-06-24",
      "type": "Out",
      "category": "Biaya Admin/Fee",
      "account": "Permata 412 (Payroll)",
      "amount": 50000,
      "desc": "Fee/denda bayar CC Permata"
    },
    {
      "id": "t30",
      "date": "2026-06-24",
      "type": "Out",
      "category": "Liability Payment - CC",
      "account": "Permata 412 (Payroll)",
      "amount": 2360448,
      "desc": "Bayar tagihan CC Permata"
    },
    {
      "id": "t29",
      "date": "2026-06-24",
      "type": "Out",
      "category": "Biaya Admin/Fee",
      "account": "BCA 730",
      "amount": 2500,
      "desc": "Admin fee intercash ke Permata 829"
    },
    {
      "id": "t28",
      "date": "2026-06-24",
      "type": "Transfer",
      "category": "Transfer Internal",
      "account": "BCA 730 -> Permata 829",
      "amount": 4500000,
      "desc": "Intercash BCA ke Permata 829"
    },
    {
      "id": "t27",
      "date": "2026-06-24",
      "type": "In",
      "category": "Income - Other",
      "account": "BCA 730",
      "amount": 4822619,
      "desc": "VOO ETF Pluang - withdraw settled"
    },
    {
      "id": "t26",
      "date": "2026-06-23",
      "type": "Out",
      "category": "Meals",
      "account": "CC CIMB",
      "amount": 31000,
      "desc": "Warteg makan"
    },
    {
      "id": "t25",
      "date": "2026-06-23",
      "type": "Out",
      "category": "Liability Payment - KTA",
      "account": "CIMB 707",
      "amount": 2837444,
      "desc": "Auto-debit KTA Xtra Dana"
    },
    {
      "id": "t24",
      "date": "2026-06-23",
      "type": "Out",
      "category": "Meals",
      "account": "BCA 730",
      "amount": 59900,
      "desc": "Beli rokok dan minuman"
    },
    {
      "id": "t23",
      "date": "2026-06-22",
      "type": "Out",
      "category": "Meals",
      "account": "BCA 730",
      "amount": 13500,
      "desc": "Kebab"
    },
    {
      "id": "t22",
      "date": "2026-06-22",
      "type": "Out",
      "category": "Transportation",
      "account": "BCA 730",
      "amount": 38783,
      "desc": "Top-up GoPay"
    },
    {
      "id": "t21",
      "date": "2026-06-22",
      "type": "Out",
      "category": "Meals",
      "account": "BCA 730",
      "amount": 25000,
      "desc": "WARUNG NAS"
    },
    {
      "id": "t20",
      "date": "2026-06-21",
      "type": "Out",
      "category": "Wellness (Hobbies & Travel)",
      "account": "BCA 730",
      "amount": 30000,
      "desc": "Main padel"
    },
    {
      "id": "t19",
      "date": "2026-06-21",
      "type": "Out",
      "category": "Biaya Admin/Fee",
      "account": "BCA 730",
      "amount": 56650,
      "desc": "GoPay Later - biaya admin"
    },
    {
      "id": "t18",
      "date": "2026-06-21",
      "type": "Out",
      "category": "Marketplace / Other",
      "account": "BCA 730",
      "amount": 187091,
      "desc": "GoPay Later - Tokopedia"
    },
    {
      "id": "t17",
      "date": "2026-06-21",
      "type": "Out",
      "category": "Service Vehicle",
      "account": "BCA 730",
      "amount": 114700,
      "desc": "Gear Girbox Gigi Speedometer"
    },
    {
      "id": "t16",
      "date": "2026-06-21",
      "type": "Out",
      "category": "Meals",
      "account": "BCA 730",
      "amount": 50000,
      "desc": "QRIS - makan malam (baso)"
    },
    {
      "id": "t15",
      "date": "2026-06-21",
      "type": "Out",
      "category": "Meals",
      "account": "BCA 730",
      "amount": 294882,
      "desc": "GoPay Later - GoFood"
    },
    {
      "id": "t14",
      "date": "2026-06-21",
      "type": "Out",
      "category": "Transportation",
      "account": "BCA 730",
      "amount": 222360,
      "desc": "GoPay Later - GoRide"
    },
    {
      "id": "t13",
      "date": "2026-06-21",
      "type": "Transfer",
      "category": "Transfer Internal",
      "account": "Permata -> BCA 730",
      "amount": 1000000,
      "desc": "Transfer internal Permata Payroll ke BCA 7305025062"
    },
    {
      "id": "t12",
      "date": "2026-06-21",
      "type": "Out",
      "category": "Meals",
      "account": "BCA 730",
      "amount": 12100,
      "desc": "ALFAMART R"
    },
    {
      "id": "t11",
      "date": "2026-06-21",
      "type": "Out",
      "category": "Service Vehicle",
      "account": "BCA 730",
      "amount": 247500,
      "desc": "T3 MOTOR - servis motor"
    },
    {
      "id": "t10",
      "date": "2026-06-21",
      "type": "Out",
      "category": "Meals",
      "account": "BCA 730",
      "amount": 26000,
      "desc": "Kabita Ane - beli jus"
    },
    {
      "id": "t9",
      "date": "2026-06-21",
      "type": "Out",
      "category": "Transportation",
      "account": "BCA 730",
      "amount": 20480,
      "desc": "SPBU 34.15 - isi bensin motor"
    },
    {
      "id": "t8",
      "date": "2026-06-21",
      "type": "Out",
      "category": "Transportation",
      "account": "BCA 730",
      "amount": 50000,
      "desc": "Top-up Flazz BCA"
    },
    {
      "id": "t7",
      "date": "2026-06-20",
      "type": "Out",
      "category": "Lain-lain / Belum Jelas",
      "account": "CC CIMB",
      "amount": 10000,
      "desc": "QR payment, merchant tidak disebutkan"
    },
    {
      "id": "t6",
      "date": "2026-06-20",
      "type": "Out",
      "category": "Transportation",
      "account": "BCA 730",
      "amount": 103075,
      "desc": "Top-up Flazz BCA"
    },
    {
      "id": "t5",
      "date": "2026-06-20",
      "type": "Out",
      "category": "Lain-lain / Belum Jelas",
      "account": "BCA 730",
      "amount": 10000,
      "desc": "QR payment - VM Yanmar"
    },
    {
      "id": "t4",
      "date": "2026-06-20",
      "type": "In",
      "category": "Income - Other",
      "account": "BCA 730",
      "amount": 70000,
      "desc": "Transfer masuk dari Lia Uzliawati SE"
    },
    {
      "id": "t3",
      "date": "2026-06-20",
      "type": "Out",
      "category": "Wellness (Hobbies & Travel)",
      "account": "BCA 730",
      "amount": 10000,
      "desc": "QR payment - Padel Geh"
    },
    {
      "id": "t2",
      "date": "2026-06-20",
      "type": "Out",
      "category": "Transportation",
      "account": "CC CIMB",
      "amount": 272200,
      "desc": "SPBU 34.158.04 KSO Curug, Tangerang"
    },
    {
      "id": "t1",
      "date": "2026-06-20",
      "type": "Transfer",
      "category": "Transfer Internal",
      "account": "Permata -> BCA 730",
      "amount": 500000,
      "desc": "Transfer internal Permata ke BCA 7305025062"
    },
    {
      "id": "t73",
      "date": "2024-03-25",
      "type": "In",
      "category": "Transfer",
      "account": "Permata 598",
      "amount": 150000,
      "desc": "Auto Debit"
    },
    {
      "id": "t72",
      "date": "2024-03-25",
      "type": "Out",
      "category": "Transfer",
      "account": "Permata 734",
      "amount": 150000,
      "desc": "Auto Debit"
    },
    {
      "id": "t71",
      "date": "2024-02-20",
      "type": "Out",
      "category": "Debit",
      "account": "Permata 598",
      "amount": 150000,
      "desc": "Debit dari rekening Permata 734"
    }
  ],
  "budgets": {
    "Kebutuhan Dasar Anak": 1700000,
    "Mainan & Edukasi Anak": 200000,
    "Meals": 1000000,
    "Listrik": 1000000,
    "Wifi & Internet": 350000,
    "Transportation": 2800000,
    "Service Vehicle": 500000,
    "Phone Credit": 200000,
    "Wellness (Hobbies & Travel)": 200000,
    "Apps & Subscriptions": 0,
    "Electronics & Accessories": 0,
    "Marketplace / Other": 300000,
    "Interest Expense - KTA": 0,
    "Interest Expense - KPR": 0,
    "Biaya Admin/Fee": 100000,
    "Lain-lain / Belum Jelas": 153000
  },
  "income": {
    "salary": 20685871,
    "kprMonthly": 7400000
  }
};

if (typeof window !== 'undefined') {
  window.EDITH_API_DATA = FINANCE_DATA;
}
