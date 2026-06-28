"""
test_routing.py — QA script untuk Edith bot routing
Run: python3 backend/test_routing.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

# Import routing logic dari bot
from telegram_bot import route, TOOL_GROUPS, MODEL_FAST, MODEL_SMART, _is_compound

# Format: (query, expected_group_key, expected_model)
TEST_CASES = [
    # --- BANK ---
    ("saldo gua berapa?",                   "bank",          MODEL_FAST),
    ("rekening gua apa aja?",               "bank",          MODEL_FAST),
    ("28 jt terdiri dari apa aja?",         "bank",          MODEL_FAST),
    ("update saldo BCA 5 juta",             "bank",          MODEL_FAST),
    # --- CC ---
    ("tagihan CC gua berapa?",              "cc",            MODEL_FAST),
    ("due date kartu kredit kapan?",        "cc",            MODEL_FAST),
    ("limit CC gua?",                       "cc",            MODEL_FAST),
    ("outstanding CC bulan ini?",           "cc",            MODEL_FAST),
    # --- LOAN ---
    ("cicilan gua total berapa?",           "loan",          MODEL_FAST),
    ("KPR sisa berapa?",                    "loan",          MODEL_FAST),
    ("KTA kapan lunas?",                    "loan",          MODEL_FAST),
    ("hutang gua berapa?",                  "loan",          MODEL_FAST),
    # --- BUDGET ---
    ("budget gua sisa berapa?",             "budget",        MODEL_FAST),
    ("gua over budget ga?",                 "budget",        MODEL_FAST),
    ("alokasi pengeluaran bulan ini?",      "budget",        MODEL_FAST),
    # --- EXPENSE ---
    ("pengeluaran gua bulan ini?",          "expense",       MODEL_FAST),
    ("habis berapa buat makan?",            "expense",       MODEL_FAST),
    ("spending gua kemana aja?",            "expense",       MODEL_FAST),
    # --- INCOME ---
    ("pemasukan gua bulan ini?",            "income",        MODEL_FAST),
    ("gaji gua udah masuk?",               "income",        MODEL_FAST),
    # --- SUMMARY ---
    ("DTI gua berapa?",                     "summary",       MODEL_FAST),
    ("cash flow gua positif ga?",           "summary",       MODEL_FAST),
    ("savings rate gua?",                   "summary",       MODEL_FAST),
    # --- NET WORTH ---
    ("net worth gua berapa?",               "networth",      MODEL_SMART),
    ("total kekayaan gua?",                 "networth",      MODEL_SMART),
    ("kekayaan bersih gua?",                "networth",      MODEL_SMART),
    # --- ASSETS ---
    ("total aset gua?",                     "assets",        MODEL_SMART),
    ("punya apa aja gua?",                  "assets",        MODEL_SMART),
    # --- TRANSACTIONS ---
    ("histori transaksi gua?",              "trx_read",      MODEL_FAST),
    ("mutasi bulan ini?",                   "trx_read",      MODEL_FAST),
    ("catat makan siang 75rb BCA",          "trx_write",     MODEL_FAST),
    ("input transaksi baru",                "trx_write",     MODEL_FAST),
    # --- RECEIVABLES ---
    ("piutang gua ada berapa?",             "receivables",   MODEL_FAST),
    ("siapa yang belum bayar ke gua?",      "receivables",   MODEL_FAST),
    # --- FIXED ASSETS ---
    ("aset tetap gua apa aja?",             "fixed_assets",  MODEL_FAST),
    ("rumah gua book value berapa?",        "fixed_assets",  MODEL_FAST),
    # --- MoM COMPARISON ---
    ("banding pengeluaran bulan ini vs bulan lalu?", "expenses_mom", MODEL_SMART),
    ("tren pengeluaran gua naik turun?",    "expenses_mom",  MODEL_SMART),
    # --- MARKET ---
    ("IHSG sekarang?",                      "market_stock",  MODEL_SMART),
    ("BBCA saham gimana?",                  "market_stock",  MODEL_SMART),
    ("BTC harga sekarang?",                 "market_crypto", MODEL_SMART),
    ("crypto gua naik ga?",                 "market_crypto", MODEL_SMART),
    ("kurs dollar sekarang?",               "market_fx",     MODEL_FAST),
    ("nilai tukar USD ke IDR?",             "market_fx",     MODEL_FAST),
    ("TA BBCA gimana?",                     "market_ta",     MODEL_SMART),
    ("RSI BTC sekarang?",                   "market_ta",     MODEL_SMART),
    ("berita market hari ini?",             "market_news",   MODEL_SMART),
    # --- INVESTMENT ---
    ("portfolio gua gimana?",               "invest_market", MODEL_SMART),
    ("P&L investasi gua?",                  "invest_pl",     MODEL_SMART),
    ("untung rugi saham gua?",              "invest_pl",     MODEL_SMART),
    ("reksadana gua berapa?",               "invest_market", MODEL_SMART),
    # --- FULL FINANCE / ADVICE ---
    ("kondisi keuangan gua gimana?",        "full_finance",  MODEL_SMART),
    ("review keuangan gua keseluruhan?",    "full_finance",  MODEL_SMART),
    ("gua layak beli saham ga?",            "advice",        MODEL_SMART),
    ("harus gimana strategi keuangan gua?", "advice",        MODEL_SMART),
    ("saran investasi dong",                "advice",        MODEL_SMART),
    # --- CRUD ---
    ("tambah bank BCA baru",                "crud_bank",     MODEL_FAST),
    ("hapus CC BCA",                        "crud_cc",       MODEL_FAST),
    ("tambah investasi baru",               "crud_investment", MODEL_FAST),
    ("update budget makan",                 "crud_budget",   MODEL_FAST),
    # --- CONFIRMATION ---
    ("ya",   None, MODEL_FAST),
    ("bener", None, MODEL_FAST),
    ("gas",  None, MODEL_FAST),
    ("oke",  None, MODEL_FAST),
    ("batal", None, MODEL_FAST),
    # --- DAILY BRIEF ---
    ("daily brief dong",                    "all",           MODEL_SMART),
]

def run_tests():
    passed = failed = 0
    failures = []

    for query, expected_group, expected_model in TEST_CASES:
        model, tools = route(query)
        tool_names = [t["function"]["name"] for t in tools]

        model_ok = (model == expected_model)

        # For confirmation words, just check model
        if expected_group is None:
            if model_ok:
                passed += 1
            else:
                failed += 1
                failures.append(f"  FAIL [{query!r}] model={model} expected={expected_model}")
            continue

        # Check if expected group's tools are a subset of returned tools
        expected_tools = [t["function"]["name"] for t in TOOL_GROUPS.get(expected_group, [])]
        group_ok = all(t in tool_names for t in expected_tools) if expected_tools else True

        if model_ok and group_ok:
            passed += 1
        else:
            failed += 1
            reason = []
            if not model_ok:   reason.append(f"model={model} expected={expected_model}")
            if not group_ok:   reason.append(f"tools={tool_names} expected_group={expected_group}({expected_tools})")
            failures.append(f"  FAIL [{query!r}] {' | '.join(reason)}")

    total = passed + failed
    print(f"\n{'='*60}")
    print(f"Edith Routing QA — {passed}/{total} passed ({round(passed/total*100)}%)")
    print(f"{'='*60}")
    if failures:
        print("\nFAILURES:")
        for f in failures:
            print(f)
    else:
        print("\n✅ All tests passed!")
    print()

COMPOUND_CASES = [
    # (query, should_be_compound)
    # TRUE — multi-write operations
    ("catat makan 75rb BCA dan parkir 10rb cash",                True),
    ("hapus transaksi t72 yang salah dan tambah lagi yang bener",True),
    ("tambah rekening Jago dan catat saldo awal 5jt",           True),
    ("update saldo BCA 5jt dan Mandiri 3jt",                    True),
    ("set budget makan 3jt dan transport 1.5jt",                True),
    ("catat gaji 15jt Mandiri dan bayar CC BCA 2jt",            True),
    ("input kopi 35rb, makan 85rb, grab 25rb — semua BCA",      True),
    ("tambah investasi BBCA dan update saldo Mandiri",          True),
    ("catat transfer ke Permata 3jt dan update saldo BCA",      True),
    ("tambah CC BRI limit 10jt dan set budget lifestyle 2jt",   True),
    # FALSE — single operations
    ("saldo gua berapa?",                                       False),
    ("networth gua berapa?",                                    False),
    ("catat makan siang 75rb BCA",                              False),
    ("hapus transaksi t72",                                     False),
    ("tambah rekening Jago",                                    False),
    ("IHSG sekarang?",                                          False),
    ("portfolio gua gimana?",                                   False),
]

def run_compound_tests():
    passed = failed = 0
    failures = []
    for query, expected in COMPOUND_CASES:
        result = _is_compound(query.lower())
        if result == expected:
            passed += 1
        else:
            failed += 1
            failures.append(f"  FAIL [{query!r}] is_compound={result} expected={expected}")

    total = passed + failed
    print(f"\n{'='*60}")
    print(f"Compound Detection QA — {passed}/{total} passed ({round(passed/total*100)}%)")
    print(f"{'='*60}")
    if failures:
        print("\nFAILURES:")
        for f in failures:
            print(f)
    else:
        print("\n✅ All compound tests passed!")
    print()

if __name__ == "__main__":
    run_tests()
    run_compound_tests()
