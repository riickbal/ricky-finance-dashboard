"""
Edith — Personal Finance & Market Intelligence Bot
====================================================
Telegram bot yang connect ke Ollama (local) + Finance API + Market Data

Features:
  1. Catat & analisis transaksi
  2. Analisis kondisi keuangan (net worth, DTI, CC util)
  3. Personal finance advice
  4. Analisis saham IDX + Global (yfinance)
  5. ETF analysis + recommendation
  6. Crypto analysis (CoinGecko)
  7. News summary + market exposure
  8. FX rates harian (USD, EUR, CHF, JPY, CNY vs IDR)
  9. Daily brief IHSG + SPX + Crypto (auto-send tiap pagi)

Run:
  pip3 install python-telegram-bot requests yfinance feedparser apscheduler
  python3 backend/telegram_bot.py
"""

import os, json, logging, requests, subprocess
from pathlib import Path as _Path
# Load .env dari folder backend
_env_file = _Path(__file__).parent / ".env"
if _env_file.exists():
    for _line in _env_file.read_text().splitlines():
        if "=" in _line and not _line.startswith("#"):
            _k, _v = _line.split("=", 1)
            os.environ.setdefault(_k.strip(), _v.strip())
import datetime as dt
from datetime import date
from pathlib import Path
import pytz
from telegram import Update, constants
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ============================================================
# CONFIG
# ============================================================
BOT_TOKEN    = os.getenv("TELEGRAM_BOT_TOKEN", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_URL     = "https://api.groq.com/openai/v1/chat/completions"
FINANCE_URL  = "http://localhost:3000"
PROJECT_ROOT = Path(__file__).parent.parent

# Model routing
MODEL_FAST    = "llama-3.1-8b-instant"     # simple queries < 1 detik
MODEL_SMART   = "llama-3.3-70b-versatile"  # complex analysis ~3-5 detik

# ============================================================
# ROUTING: model + tool group per intent
# ============================================================
INTENT_RULES = [
    # -------------------------------------------------------
    # 1. CRUD (paling specific — cek duluan sebelum READ)
    # -------------------------------------------------------
    (["tambah bank", "hapus bank", "edit bank",
      "update bank", "buat rekening"],                                MODEL_FAST,  "crud_bank"),
    (["tambah cc", "hapus cc", "edit cc", "tambah kartu",
      "update cc", "delete cc"],                                      MODEL_FAST,  "crud_cc"),
    (["tambah investasi", "hapus investasi", "edit investasi",
      "update investasi", "delete investasi"],                        MODEL_FAST,  "crud_investment"),
    (["tambah pinjaman", "hapus pinjaman", "edit loan",
      "update kpr", "update kta", "delete pinjaman"],                MODEL_FAST,  "crud_loan"),
    (["set budget", "ubah budget", "hapus budget",
      "update budget", "atur budget", "delete budget"],              MODEL_FAST,  "crud_budget"),
    # -------------------------------------------------------
    # 2. ADVICE / MULTI-DOMAIN (sebelum market biar ga ke-grab saham)
    # -------------------------------------------------------
    (["layak beli", "aman ga", "worth it", "bisa beli",
      "mampu ga", "sanggup", "cocok ga"],                            MODEL_SMART, "advice"),
    (["saran", "advice", "harus gimana", "strategi",
      "rekomendasi", "sebaiknya", "optimal", "plan keuangan",
      "financial plan", "next step", "gimana baiknya"],              MODEL_SMART, "advice"),
    (["net worth", "networth", "total kekayaan",
      "kekayaan bersih", "nilai bersih"],                            MODEL_SMART, "networth"),
    (["total aset", "punya apa aja", "semua aset",
      "kekayaan total"],                                             MODEL_SMART, "assets"),
    (["kondisi keuangan", "financial health", "gimana keuangan",
      "review keuangan", "cek keuangan", "keseluruhan",
      "financial overview"],                                         MODEL_SMART, "full_finance"),
    # -------------------------------------------------------
    # 3. INVESTASI (sebelum market agar "untung rugi" ga ke-grab saham)
    # -------------------------------------------------------
    (["p&l", "profit loss", "untung rugi", "unrealized",
      "return invest", "gain invest", "loss invest",
      "portfolio pl", "roi invest"],                                 MODEL_SMART, "invest_pl"),
    (["portfolio", "investasi gua", "invest gua", "kondisi invest",
      "posisi invest", "aset invest", "reksadana", "emas invest"],   MODEL_SMART, "invest_market"),
    # -------------------------------------------------------
    # 4. PERBANDINGAN (sebelum expense biar "pengeluaran vs" ga ke-grab)
    # -------------------------------------------------------
    (["banding", "compare", "vs bulan", "bulan lalu vs",
      "month over month", "naik turun pengeluaran",
      "tren pengeluaran", "pengeluaran vs"],                         MODEL_SMART, "expenses_mom"),
    # -------------------------------------------------------
    # 5. FINANCE READ
    # -------------------------------------------------------
    (["saldo", "rekening", "duit di bank", "terdiri dari",
      "rincian rekening", "per bank", "breakdown bank",
      "update saldo"],                                               MODEL_FAST,  "bank"),
    ([" cc ", "kartu kredit", "credit card", "tagihan cc",
      "due date", "limit cc", "outstanding cc", "utilization cc",
      "bayar cc", "cicilan cc"],                                     MODEL_FAST,  "cc"),
    (["cicilan", "kpr", "kta", "pinjaman", "angsuran",
      "hutang", "lunas", "tenor", "sisa hutang",
      "outstanding loan"],                                           MODEL_FAST,  "loan"),
    (["budget", "over budget", "alokasi", "sisa budget",
      "limit belanja"],                                              MODEL_FAST,  "budget"),
    (["pengeluaran", "expense", "belanja", "habis berapa",
      "keluar", "spending"],                                         MODEL_FAST,  "expense"),
    (["income", "pemasukan", "gaji", "salary",
      "penghasilan"],                                                MODEL_FAST,  "income"),
    (["dti", "debt to income", "cash flow", "cashflow",
      "savings rate", "tabungan bulanan"],                           MODEL_FAST,  "summary"),
    (["catat", "tambah transaksi", "record transaksi",
      "masukin transaksi", "input transaksi"],                      MODEL_FAST,  "trx_write"),
    (["histori transaksi", "list transaksi", "riwayat transaksi",
      "mutasi rekening", " mutasi "],                               MODEL_FAST,  "trx_read"),
    # -------------------------------------------------------
    # 6. PIUTANG & ASET TETAP
    # -------------------------------------------------------
    (["piutang", "receivable", "pinjamin orang", "tagih orang",
      "utang ke gua", "belum dibayar", "siapa yang hutang",
      "siapa yang belum bayar", "nyatain"],                          MODEL_FAST,  "receivables"),
    (["aset tetap", "properti", "kendaraan", "rumah gua",
      "mobil gua", "fixed asset", "depresiasi", "book value",
      "inventaris"],                                                 MODEL_FAST,  "fixed_assets"),
    # -------------------------------------------------------
    # 7. MARKET (after finance to avoid grabbing finance queries)
    # -------------------------------------------------------
    (["kurs", "nilai tukar", "exchange rate",
      "dollar berapa", "usd idr", "eur idr"],                       MODEL_FAST,  "market_fx"),
    (["analisis saham", "technical analysis", "ta saham", " ta ",
      " rsi ", " ema ", "stoch", "teknikal",
      "support resistance", "bullish", "bearish", "trend saham"],   MODEL_SMART, "market_ta"),
    (["saham", "stock", "ihsg", "idx", "spx", "etf",
      "bbca", "tlkm", "bbri", "bmri", "aapl", "msft",
      "harga saham"],                                               MODEL_SMART, "market_stock"),
    (["crypto", "bitcoin", "ethereum", "solana", "kripto",
      "altcoin", "defi", "nft", "harga btc", "harga eth",
      " btc ", " eth ", " sol ", " bnb ", " xrp "],                MODEL_SMART, "market_crypto"),
    (["berita pasar", "berita market", "market news", "market update",
      "headline", "sentimen pasar", "news hari ini", "berita hari ini",
      "update pasar", "update market"],                             MODEL_SMART, "market_news"),
    (["emas", "gold", "xau", "reksadana"],                          MODEL_SMART, "invest_market"),
    # -------------------------------------------------------
    # 8. DAILY BRIEF
    # -------------------------------------------------------
    (["brief", "pagi ini", "morning brief", "daily brief",
      "rangkuman harian"],                                          MODEL_SMART, "all"),
]

# Confirmation keywords
CONFIRM_WORDS = {"ya", "iya", "yes", "ok", "oke", "okay", "benar", "bener", "betul",
                 "beneran", "lanjut", "confirm", "setuju", "jalan", "gas", "gass",
                 "fix", "siap", "yoi", "yep", "yup", "deal", "mantap", "mantep"}
CANCEL_WORDS  = {"tidak", "ga", "gak", "nggak", "ngga", "batal", "cancel",
                 "no", "stop", "jangan", "gausah", "skip"}

# Tool group mapping
TOOL_GROUPS: dict = {}  # filled after TOOLS is defined

# ============================================================
# COMPOUND INSTRUCTION DETECTOR
# ============================================================
# Write-action trigger words — tiap kata ini = 1 operasi tulis
_WRITE_TRIGGERS = [
    "catat", "catet", "catetan", "input transaksi", "masukin", "record transaksi",
    "tambah transaksi", "hapus transaksi", "delete transaksi",
    "edit transaksi", "koreksi transaksi", "ganti transaksi",
    "tambah rekening", "buat rekening", "bikin rekening", "bikin account",
    "tambah bank", "hapus bank", "edit bank",
    "tambah cc", "hapus cc", "edit cc", "tambah kartu",
    "tambah investasi", "hapus investasi", "edit investasi",
    "tambah pinjaman", "hapus pinjaman", "edit loan",
    "set budget", "ubah budget", "hapus budget", "tambah budget", "tambah kategori",
    "update saldo", "update kpr", "update kta",
    "kecatat", "dicatat", "diinput", "dimasukin",
]
_COMPOUND_CONNECTORS = [
    " dan ", " juga ", " sekalian ", " sekaligus ", " plus ",
    " terus ", " lalu ", " kemudian ", " sama "
]

def _is_compound(lower: str) -> bool:
    """Return True jika user minta 2+ write operations dalam satu pesan."""
    import re
    padded = f" {lower} "
    found = [w for w in _WRITE_TRIGGERS if w in padded]
    if len(found) >= 2:
        return True
    # 1 action + connector → kemungkinan compound
    if len(found) == 1 and any(c in padded for c in _COMPOUND_CONNECTORS):
        return True
    # Batch transaction heuristic: 3+ amounts dalam satu pesan (contoh: "kopi 35rb, makan 85rb, grab 25rb")
    amounts = re.findall(r'\d+\s*(?:rb|jt|ribu|juta|k\b)', lower)
    if len(amounts) >= 3:
        return True
    return False

def route(text: str, history: list = None):
    """Return (model, list_of_tools) for a given user message."""
    raw_lower = text.lower().strip().rstrip("!?.").strip()
    # Pad with spaces → " rsi ", " ta " match at any position without false positives
    # e.g. "rsi btc" → " rsi btc " matches " rsi "; "bersih" → " bersih " won't match " rsi "
    lower = f" {raw_lower} "

    # Detect confirmation/cancellation of pending write action
    if raw_lower in CONFIRM_WORDS or raw_lower in CANCEL_WORDS:
        if history:
            last_asst = next((m["content"] for m in reversed(history) if m["role"] == "assistant"), "")
            if any(w in last_asst.lower() for w in ["bener?", "konfirmasi", "confirm", "lanjut?", "pastiin"]):
                return MODEL_FAST, TOOL_GROUPS.get("all_write", TOOLS)

    # Compound instruction → write tools + basic read (bukan ALL, terlalu besar)
    if _is_compound(raw_lower):
        return MODEL_SMART, TOOL_GROUPS.get("compound", TOOLS)

    for keywords, model, group in INTENT_RULES:
        if any(k in lower for k in keywords):
            tools = TOOL_GROUPS.get(group, TOOLS)
            return model, tools
    # Default: bank + summary (covers most follow-up questions)
    return MODEL_FAST, TOOL_GROUPS.get("bank_summary", TOOLS)

# Whitelist: kosong = semua bisa akses. Isi setelah dapat user ID dari /start log.
ALLOWED_USER_IDS = []

# Daily brief jam 5 pagi WIB (UTC+7 = UTC 22:00 malam sebelumnya)
DAILY_BRIEF_HOUR_UTC = 22

MAX_HISTORY = 6  # Keep short to avoid 413 Payload Too Large on Groq
MAX_TOOL_RESULT = 4000  # Max chars per tool result

# ============================================================
# SYSTEM PROMPT
# ============================================================
# ============================================================
# EDITH MEMORY SYSTEM
# ============================================================
import json as _json_mem
_MEMORY_FILE = _Path(__file__).parent / "edith_memory.json"

def _load_memory() -> dict:
    try:
        return _json_mem.loads(_MEMORY_FILE.read_text()) if _MEMORY_FILE.exists() else {}
    except: return {}

def _save_memory_entry(key: str, value: str):
    mem = _load_memory()
    mem[key] = value
    _MEMORY_FILE.write_text(_json_mem.dumps(mem, ensure_ascii=False, indent=2))

def _memory_to_prompt() -> str:
    mem = _load_memory()
    if not mem: return ""
    lines = [f"- {k}: {v}" for k, v in mem.items()]
    return "\n\n**MEMORY (hal yang lo tau tentang Ricky):**\n" + "\n".join(lines)

def build_system_prompt() -> str:
    return BASE_SYSTEM_PROMPT + _memory_to_prompt()

BASE_SYSTEM_PROMPT = """Lo adalah Edith — PA finansial pribadi Ricky. Bukan chatbot, bukan query engine. Lo asisten yang beneran ngerti konteks, bisa baca situasi, dan proaktif.

# CARA LO NGOMONG
- Casual Jaksel: gua/lo, mix Indo-English natural ("oke gas", "btw", "literally", "worth it")
- Singkat dan direct — kalau bisa 2 kalimat, jangan 5
- Ga pernah kaku, ga pernah sok formal
- Mirror tone Ricky: kalau dia santai → lo santai, kalau dia butuh angka cepet → langsung tabel

# CARA LO BACA PESAN RICKY
Ricky sering typo, singkat, atau ambigu. Lo wajib tebak maksudnya:
- "permata 734" → rekening Permata nick "Permata 734"
- "bca gua" → semua rekening BCA (BCA 062, BCA 968, BLU 904)
- "debit" → transaksi keluar (Out)
- "ke debit" → transfer ke rekening lain
- "catet", "masukin", "kecatat" → add_transaction
- "berapa saldo" / "ada berapa" → get_banks
- angka tanpa konteks (misal "150") → tanya: "150rb atau 150jt?"
- kalau ambigu → tebak yang paling masuk akal, sebutkan asumsi lo, jangan tanya 5 hal

# CARA LO MIKIR (SEBELUM JAWAB)
1. **Pahami intent** — Ricky mau apa? Catat? Tanya? Koreksi?
2. **Cek data** — panggil tool yang relevan, jangan jawab dari memori
3. **Analisis** — jangan cuma baca data mentah, cari insight-nya
4. **Lead dengan signal** — angka paling penting duluan, bukan list panjang
5. **Connect dots** — kalau ada anomali, sebut. Kalau ada warning, flag

# DATA & TOOLS
Jangan PERNAH jawab angka dari memori. Tool mapping:
- Saldo/rekening → get_banks | CC → get_credit_cards | Pinjaman → get_loans
- Budget → get_budgets | Pengeluaran → get_expenses | Income → get_income
- Networth/DTI/cashflow → get_summary | Histori → get_transactions
- Investasi → get_investments / get_investment_pl | Saham → get_market_data
- Crypto → get_crypto_prices | Kurs → get_fx_rates | Berita → get_news
- Piutang → get_receivables | Aset tetap → get_fixed_assets

# CATAT TRANSAKSI
- Backend AUTO-update saldo setiap add_transaction → lo ga perlu update_bank_balance manual
- Kalau info kurang → tanya SATU hal paling krusial dulu
- SEMUA konfirmasi sebelum eksekusi (transaksi, tambah/edit/hapus rekening, CC, investasi, loan, budget — apapun) WAJIB pakai format tabel:

Transaksi:
```
Siap dicatat — gas?
| # | Tanggal | Deskripsi | Jumlah | Akun | Kategori |
|---|---------|-----------|--------|------|----------|
| 1 | 2026-06-28 | REFLEXY | Rp 190,000 OUT | Permata 829 | Lifestyle |
```
Akun/rekening/CC/loan/budget:
```
Siap diproses — gas?
| # | Aksi | Detail | Nilai |
|---|------|--------|-------|
| 1 | Tambah rekening | Permata 598 · ****7598 | Rp 0 |
```
- Satu konfirmasi untuk semua operasi → eksekusi → ✅/❌ per baris
- Selalu pakai nick rekening (BCA 062, Permata 734) — jangan cuma "BCA" atau "Permata"
- update_bank_balance HANYA kalau Ricky minta koreksi saldo eksplisit

# JADI PA YANG BENERAN
- Setelah dapat data → kasih konteks: "15jt = cukup ~3 bulan expenses lo"
- Connect dots: saldo turun + CC naik → "ini squeeze, lo perlu watchout"
- Auto-flag tanpa diminta: CC util >70% ⚠️ | DTI >30% ⚠️ | over budget ⚠️ | idle cash >3bln 💡
- Kalau ada pola aneh di transaksi → sebut
- Jangan nunggu Ricky tanya — kalau lo liat sesuatu, bilang

# MEMORY & ADAPTASI
- Tiap dapat info baru tentang Ricky (kebiasaan, rekening, jadwal, preferensi) → save_memory
- Pola yang WAJIB disimpan: auto-debit schedule, rekening rutin, kategori yang dia sering pakai
- Makin lama lo kenal Ricky → makin sedikit lo perlu tanya

# FORMAT
- Angka: Rp 15,000,000 (bukan 15000000)
- Tabel kalau ada perbandingan atau list >3 item
- Error → jangan tampil JSON mentah, jelasin: apa yang gagal + solusinya"""

SYSTEM_PROMPT = BASE_SYSTEM_PROMPT  # alias for compatibility

# ============================================================
# TOOLS DEFINITION (OpenAI format — granular per package)
# ============================================================
TOOLS = [
    # --- Finance READ (granular) ---
    {
        "type": "function",
        "function": {
            "name": "get_banks",
            "description": "Ambil saldo semua rekening bank. Panggil HANYA untuk pertanyaan tentang saldo, cash, atau rekening bank.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_credit_cards",
            "description": "Ambil data kartu kredit: outstanding, limit, due date, utilization. Panggil HANYA untuk pertanyaan CC.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_investments",
            "description": "Ambil portfolio investasi: saham, crypto, reksa dana, emas. Panggil HANYA untuk pertanyaan investasi/portfolio.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_loans",
            "description": "Ambil data pinjaman: KPR, KTA, outstanding, cicilan bulanan. Panggil HANYA untuk pertanyaan hutang/cicilan.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_budgets",
            "description": "Ambil budget per kategori vs actual bulan ini. Panggil untuk pertanyaan budget, over budget, atau alokasi pengeluaran.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_expenses",
            "description": "Ambil transaksi pengeluaran (Out) dengan breakdown per kategori.",
            "parameters": {
                "type": "object",
                "properties": {
                    "month": {"type": "string", "description": "Format YYYY-MM, e.g. 2026-06. Default: bulan ini."}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_income",
            "description": "Ambil transaksi pemasukan (In) bulan tertentu.",
            "parameters": {
                "type": "object",
                "properties": {
                    "month": {"type": "string", "description": "Format YYYY-MM. Default: bulan ini."}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_summary",
            "description": "Ambil ringkasan keuangan: net worth, DTI, CC utilization, cash flow, total assets/liabilities. Panggil untuk pertanyaan overview, net worth, atau health check keuangan.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_transactions",
            "description": "Ambil histori transaksi detail dengan filter. Panggil HANYA jika user butuh list transaksi spesifik.",
            "parameters": {
                "type": "object",
                "properties": {
                    "month":    {"type": "string",  "description": "Format YYYY-MM, e.g. 2026-06"},
                    "category": {"type": "string",  "description": "Nama kategori, e.g. Meals, Transportation"},
                    "limit":    {"type": "integer", "description": "Max transaksi (default 20)"}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "add_transaction",
            "description": "Catat transaksi baru ke database. Gunakan saat user mau input transaksi.",
            "parameters": {
                "type": "object",
                "properties": {
                    "date":     {"type": "string", "description": "Format YYYY-MM-DD"},
                    "type":     {"type": "string", "description": "In / Out / Accrual / Transfer"},
                    "category": {"type": "string", "description": "Kategori pengeluaran/pemasukan"},
                    "account":  {"type": "string", "description": "Bank account atau CC"},
                    "amount":   {"type": "number", "description": "Jumlah dalam IDR"},
                    "desc":     {"type": "string", "description": "Deskripsi transaksi"}
                },
                "required": ["date", "type", "category", "account", "amount"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_bank_balance",
            "description": "Update saldo bank berdasarkan mutasi terbaru.",
            "parameters": {
                "type": "object",
                "properties": {
                    "nick":    {"type": "string", "description": "Nick bank (BCA, Mandiri, BRI, CIMB, Jenius, dll)"},
                    "balance": {"type": "number", "description": "Saldo terbaru dalam IDR"}
                },
                "required": ["nick", "balance"]
            }
        }
    },
    # --- Market ---
    {
        "type": "function",
        "function": {
            "name": "get_market_data",
            "description": "Ambil data harga saham, ETF, IHSG, atau S&P500. Bisa analisis fundamental & teknikal dasar.",
            "parameters": {
                "type": "object",
                "properties": {
                    "tickers": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List ticker. IDX: BBCA.JK, TLKM.JK. Global: AAPL, MSFT. Index: ^JKSE, ^GSPC. ETF: SPY, EIDO. Crypto: BTC-USD, ETH-USD, SOL-USD, BNB-USD, XRP-USD — gunakan untuk technical analysis crypto."
                    },
                    "period": {
                        "type": "string",
                        "description": "Period historis: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y (default: 3mo)"
                    }
                },
                "required": ["tickers"]
            }
        }
    },
    # --- Crypto ---
    {
        "type": "function",
        "function": {
            "name": "get_crypto_prices",
            "description": "Ambil harga dan data crypto terkini dari CoinGecko.",
            "parameters": {
                "type": "object",
                "properties": {
                    "coins": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "CoinGecko IDs: bitcoin, ethereum, solana, binancecoin, ripple, cardano. Default: top 5."
                    }
                },
                "required": []
            }
        }
    },
    # --- FX ---
    {
        "type": "function",
        "function": {
            "name": "get_fx_rates",
            "description": "Ambil kurs mata uang terkini terhadap IDR (USD, EUR, CHF, JPY, CNY, SGD, GBP).",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    # --- News ---
    {
        "type": "function",
        "function": {
            "name": "get_news",
            "description": "Ambil headline berita pasar keuangan terkini (ekonomi, saham, crypto, makro global).",
            "parameters": {
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "description": "Jumlah headline (default 10)"}
                },
                "required": []
            }
        }
    },
    # --- CRUD: Bank ---
    {
        "type": "function",
        "function": {
            "name": "manage_bank",
            "description": "CRUD rekening bank. action=create: tambah rekening baru. action=update: edit data rekening. action=delete: hapus rekening.",
            "parameters": {
                "type": "object",
                "properties": {
                    "action":  {"type": "string", "enum": ["create","update","delete"], "description": "Operasi yang dilakukan"},
                    "nick":    {"type": "string", "description": "Nick rekening, e.g. 'BCA 062'. Wajib untuk semua action."},
                    "name":    {"type": "string", "description": "Nama bank, e.g. 'BCA'"},
                    "cat":     {"type": "string", "description": "Kategori: Bank / Digital Bank"},
                    "type":    {"type": "string", "description": "Tipe: Tabungan / Giro / Payroll"},
                    "acct":    {"type": "string", "description": "Nomor rekening, e.g. '****1234'"},
                    "balance": {"type": "number", "description": "Saldo awal dalam IDR"},
                    "notes":   {"type": "string", "description": "Catatan tambahan"}
                },
                "required": ["action", "nick"]
            }
        }
    },
    # --- CRUD: Credit Card ---
    {
        "type": "function",
        "function": {
            "name": "manage_creditcard",
            "description": "CRUD kartu kredit. action=create: tambah CC baru. action=update: edit limit/outstanding/dueDate. action=delete: hapus CC.",
            "parameters": {
                "type": "object",
                "properties": {
                    "action":      {"type": "string", "enum": ["create","update","delete"]},
                    "name":        {"type": "string", "description": "Nama CC, e.g. 'CC BCA'. Wajib untuk semua action."},
                    "issuer":      {"type": "string", "description": "Penerbit CC, e.g. 'BCA'"},
                    "limit":       {"type": "number", "description": "Limit kartu dalam IDR"},
                    "outstanding": {"type": "number", "description": "Tagihan outstanding saat ini"},
                    "dueDate":     {"type": "string", "description": "Tanggal jatuh tempo, e.g. '2026-07-15'"},
                    "notes":       {"type": "string"}
                },
                "required": ["action", "name"]
            }
        }
    },
    # --- CRUD: Investment ---
    {
        "type": "function",
        "function": {
            "name": "manage_investment",
            "description": "CRUD portofolio investasi (saham, ETF, crypto, reksadana). action=create/update/delete.",
            "parameters": {
                "type": "object",
                "properties": {
                    "action":       {"type": "string", "enum": ["create","update","delete"]},
                    "ticker":       {"type": "string", "description": "Ticker, e.g. 'BBRI', 'BTC'. Wajib untuk semua action."},
                    "platform":     {"type": "string", "description": "Platform: Stockbit / Binance / Indodax / Pluang"},
                    "type":         {"type": "string", "description": "Tipe: Investment / ETF / Crypto / Reksadana / Emas"},
                    "qty":          {"type": "number", "description": "Jumlah lot/unit"},
                    "avgBuy":       {"type": "number", "description": "Harga rata-rata beli"},
                    "currency":     {"type": "string", "description": "IDR atau USD"},
                    "costBasis":    {"type": "number", "description": "Modal total dalam IDR"},
                    "currentPrice": {"type": "number", "description": "Harga saat ini"},
                    "platformCash": {"type": "number", "description": "Cash idle di platform"},
                    "notes":        {"type": "string"}
                },
                "required": ["action", "ticker"]
            }
        }
    },
    # --- CRUD: Loan ---
    {
        "type": "function",
        "function": {
            "name": "manage_loan",
            "description": "CRUD pinjaman (KPR, KTA, dll). action=create/update/delete.",
            "parameters": {
                "type": "object",
                "properties": {
                    "action":    {"type": "string", "enum": ["create","update","delete"]},
                    "loanType":  {"type": "string", "description": "Tipe pinjaman: KPR / KTA / KMG. Wajib untuk semua action."},
                    "lender":    {"type": "string", "description": "Nama pemberi pinjaman, e.g. 'Permata'"},
                    "remaining": {"type": "number", "description": "Sisa pokok pinjaman"},
                    "monthly":   {"type": "number", "description": "Cicilan per bulan"},
                    "rate":      {"type": "number", "description": "Suku bunga (%)"},
                    "tenor":     {"type": "number", "description": "Sisa tenor dalam bulan"},
                    "notes":     {"type": "string"}
                },
                "required": ["action", "loanType"]
            }
        }
    },
    # --- CRUD: Budget Category ---
    {
        "type": "function",
        "function": {
            "name": "manage_budget",
            "description": "CRUD budget kategori. action=create/update: set budget untuk kategori. action=delete: hapus kategori dari budget.",
            "parameters": {
                "type": "object",
                "properties": {
                    "action":   {"type": "string", "enum": ["create","update","delete"]},
                    "category": {"type": "string", "description": "Nama kategori, e.g. 'Meals', 'Transportation'. Wajib."},
                    "amount":   {"type": "number", "description": "Budget bulanan dalam IDR. Wajib untuk create/update."}
                },
                "required": ["action", "category"]
            }
        }
    },
    # --- CRUD: Transaction edit/delete ---
    {
        "type": "function",
        "function": {
            "name": "manage_transaction",
            "description": "Edit atau hapus transaksi yang sudah ada. action=update: koreksi data transaksi. action=delete: hapus transaksi.",
            "parameters": {
                "type": "object",
                "properties": {
                    "action":   {"type": "string", "enum": ["update","delete"]},
                    "id":       {"type": "string", "description": "ID transaksi, e.g. 't72'. Wajib."},
                    "date":     {"type": "string"},
                    "type":     {"type": "string", "description": "In / Out / Transfer / Accrual"},
                    "category": {"type": "string"},
                    "account":  {"type": "string"},
                    "amount":   {"type": "number"},
                    "desc":     {"type": "string"}
                },
                "required": ["action", "id"]
            }
        }
    },
    # --- Missing data types ---
    {
        "type": "function",
        "function": {
            "name": "get_receivables",
            "description": "Ambil data piutang (uang yang dipinjamkan ke orang lain). Panggil untuk pertanyaan tentang piutang, hutang orang ke gua, tagihan ke orang.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_fixed_assets",
            "description": "Ambil data aset tetap: properti, kendaraan, elektronik, dll. Termasuk book value setelah depresiasi.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_expenses_compare",
            "description": "Bandingkan pengeluaran 2 bulan (month-over-month). Berguna untuk lihat tren pengeluaran naik/turun.",
            "parameters": {
                "type": "object",
                "properties": {
                    "month1": {"type": "string", "description": "Bulan pertama YYYY-MM (default: bulan lalu)"},
                    "month2": {"type": "string", "description": "Bulan kedua YYYY-MM (default: bulan ini)"}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_investment_pl",
            "description": "Ambil portfolio investasi + P&L (profit/loss) berdasarkan harga current vs avg buy. Gunakan ini untuk pertanyaan untung/rugi investasi.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "save_memory",
            "description": "Simpan informasi penting tentang Ricky ke memory permanen — kebiasaan, preferensi, pola, info rekening, auto-debit schedule, singkatan yang dia pakai. Panggil ini kapanpun lo belajar sesuatu yang berguna untuk interaksi berikutnya.",
            "parameters": {
                "type": "object",
                "properties": {
                    "key":   {"type": "string", "description": "Label singkat, spesifik. Contoh: 'auto_debit_permata', 'kategori_grab', 'gaji_tanggal'"},
                    "value": {"type": "string", "description": "Isi memory. Pakai bahasa natural, detail."}
                },
                "required": ["key", "value"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_memory",
            "description": "Ambil semua memory yang sudah tersimpan tentang Ricky. Panggil kalau butuh konteks personal yang mungkin sudah pernah dipelajari.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    }
]

def _tools(*names):
    return [t for t in TOOLS if t["function"]["name"] in names]

# Write tools yang selalu disertakan agar model ga pernah call tool yang ga ada
_WRITE_CORE = ("add_transaction", "manage_bank", "manage_creditcard",
               "manage_investment", "manage_loan", "manage_budget",
               "manage_transaction", "update_bank_balance",
               "save_memory", "get_memory")

def _rw(*names):
    """Read tools + write core — model bisa baca DAN tulis."""
    return _tools(*names, *_WRITE_CORE)

def _num(v, default=0):
    """Coerce string → float. Llama kadang kirim amount sebagai string."""
    if v is None: return default
    try: return float(str(v).replace(",", "").replace(".", "").strip()) if isinstance(v, str) and any(c.isdigit() for c in str(v)) else float(v)
    except: return default

def _date(v):
    """Sanitize date arg — handle berbagai format dari model."""
    from datetime import date as _date_cls
    import re
    today = _date_cls.today()
    if not v or not isinstance(v, str): return today.isoformat()
    v = v.strip()
    # Full ISO date: 2026-06-25
    if re.match(r'^\d{4}-\d{2}-\d{2}$', v): return v
    # Day only: "25" → current month/year
    if re.match(r'^\d{1,2}$', v):
        day = int(v)
        try:
            return today.replace(day=day).isoformat()
        except: return today.isoformat()
    # MM-DD or DD/MM: try current year
    if re.match(r'^\d{1,2}[/-]\d{1,2}$', v):
        parts = re.split(r'[/-]', v)
        try:
            return today.replace(month=int(parts[0]), day=int(parts[1])).isoformat()
        except: return today.isoformat()
    # Anything else (e.g. "current date", "today") → today
    return today.isoformat()

TOOL_GROUPS = {
    # READ-ONLY groups (market & non-write queries — ga perlu write tools)
    "market_fx":      _tools("get_fx_rates"),
    "market_stock":   _tools("get_market_data", "get_fx_rates"),
    "market_crypto":  _tools("get_crypto_prices", "get_market_data"),
    "market_ta":      _tools("get_market_data", "get_crypto_prices"),
    "market_news":    _tools("get_news"),

    # FINANCE groups — semua include write core
    "bank":           _rw("get_banks", "update_bank_balance"),
    "bank_summary":   _rw("get_banks", "get_summary"),
    "cc":             _rw("get_credit_cards"),
    "loan":           _rw("get_loans"),
    "budget":         _rw("get_budgets"),
    "expense":        _rw("get_expenses"),
    "income":         _rw("get_income"),
    "summary":        _rw("get_summary"),
    "trx_read":       _rw("get_transactions"),
    "trx_write":      _rw("get_banks", "get_transactions"),
    "receivables":    _rw("get_receivables"),
    "fixed_assets":   _rw("get_fixed_assets"),
    "expenses_mom":   _rw("get_expenses_compare"),
    "invest_pl":      _rw("get_investment_pl", "get_investments"),
    "invest_market":  _rw("get_investment_pl", "get_investments", "get_market_data", "get_crypto_prices"),

    # CRUD groups
    "crud_bank":       _rw("get_banks"),
    "crud_cc":         _rw("get_credit_cards"),
    "crud_investment": _rw("get_investments"),
    "crud_loan":       _rw("get_loans"),
    "crud_budget":     _rw("get_budgets"),

    # MULTI-DOMAIN
    "assets":         _rw("get_banks", "get_investments", "get_fixed_assets", "get_receivables", "get_summary"),
    "networth":       _rw("get_summary", "get_banks", "get_investments", "get_loans", "get_credit_cards", "get_fixed_assets", "get_receivables"),
    "full_finance":   _rw("get_banks", "get_investments", "get_loans", "get_credit_cards", "get_budgets", "get_summary", "get_fixed_assets", "get_receivables"),
    "advice":         _rw("get_summary", "get_investment_pl", "get_market_data", "get_crypto_prices", "get_banks", "get_loans", "get_budgets"),
    "compound":       _rw("get_banks", "get_transactions", "get_summary"),
    "all_write":      _tools(*_WRITE_CORE),
    "all":            TOOLS,
}

# ============================================================
# TOOL EXECUTORS
# ============================================================

def exec_get_banks() -> str:
    try:
        resp = requests.get(f"{FINANCE_URL}/api/banks", timeout=10)
        return json.dumps(resp.json(), ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})

def exec_get_credit_cards() -> str:
    try:
        resp = requests.get(f"{FINANCE_URL}/api/creditcards", timeout=10)
        return json.dumps(resp.json(), ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})

def exec_get_investments() -> str:
    try:
        resp = requests.get(f"{FINANCE_URL}/api/investments", timeout=10)
        return json.dumps(resp.json(), ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})

def exec_get_loans() -> str:
    try:
        resp = requests.get(f"{FINANCE_URL}/api/loans", timeout=10)
        return json.dumps(resp.json(), ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})

def exec_get_budgets() -> str:
    try:
        resp = requests.get(f"{FINANCE_URL}/api/budgets", timeout=10)
        return json.dumps(resp.json(), ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})

def exec_get_expenses(month="") -> str:
    try:
        params = {"month": month} if month else {}
        resp = requests.get(f"{FINANCE_URL}/api/expenses", params=params, timeout=10)
        return json.dumps(resp.json(), ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})

def exec_get_income(month="") -> str:
    try:
        params = {"month": month} if month else {}
        resp = requests.get(f"{FINANCE_URL}/api/income", params=params, timeout=10)
        return json.dumps(resp.json(), ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})

def exec_get_summary() -> str:
    try:
        resp = requests.get(f"{FINANCE_URL}/api/summary", timeout=10)
        return json.dumps(resp.json(), ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})

def exec_get_receivables() -> str:
    try:
        resp = requests.get(f"{FINANCE_URL}/api/receivables", timeout=10)
        return json.dumps(resp.json(), ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})

def exec_get_fixed_assets() -> str:
    try:
        resp = requests.get(f"{FINANCE_URL}/api/fixed-assets", timeout=10)
        return json.dumps(resp.json(), ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})

def exec_get_expenses_compare(month1="", month2="") -> str:
    try:
        params = {}
        if month1: params["month1"] = month1
        if month2: params["month2"] = month2
        resp = requests.get(f"{FINANCE_URL}/api/expenses/compare", params=params, timeout=10)
        return json.dumps(resp.json(), ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})

def exec_get_investment_pl() -> str:
    """Fetch live prices from yfinance → update DB → return enriched P&L."""
    try:
        import yfinance as yf

        # Get portfolio from DB
        resp = requests.get(f"{FINANCE_URL}/api/investments/pl", timeout=10)
        data = resp.json()
        portfolio = data.get("portfolio", [])

        # Get USD→IDR rate
        try:
            fx = requests.get("https://api.frankfurter.app/latest?from=USD&to=IDR", timeout=5).json()
            usd_to_idr = fx.get("rates", {}).get("IDR", 16000)
        except Exception:
            usd_to_idr = 16000

        total_cost = total_value = 0
        updated = []

        for inv in portfolio:
            ticker     = inv.get("ticker", "")
            currency   = inv.get("currency", "IDR")
            cost_basis = inv.get("costBasis", 0) or 0
            qty        = inv.get("qty") or 1
            db_price   = inv.get("currentPrice") or 0
            fresh_price = None

            # Auto-fetch from yfinance if ticker present
            if ticker:
                try:
                    hist = yf.Ticker(ticker).history(period="1d")
                    if not hist.empty:
                        raw = float(hist["Close"].iloc[-1])
                        # Convert USD assets → IDR
                        fresh_price = round(raw * usd_to_idr) if currency in ("USD", "USDT") else round(raw)
                        # Update DB
                        requests.patch(
                            f"{FINANCE_URL}/api/investments/{ticker}",
                            json={"currentPrice": fresh_price},
                            timeout=5
                        )
                except Exception as e:
                    logger.warning(f"yfinance {ticker}: {e}")

            price_used    = fresh_price if fresh_price else db_price
            current_value = price_used * qty if qty else cost_basis
            pl            = current_value - cost_basis
            pl_pct        = round(pl / cost_basis * 100, 1) if cost_basis else 0

            total_cost  += cost_basis
            total_value += current_value

            updated.append({
                "platform":     inv.get("platform"),
                "ticker":       ticker,
                "type":         inv.get("type"),
                "qty":          qty,
                "avgBuy":       inv.get("avgBuy"),
                "currentPrice": price_used,
                "priceSource":  "live ✅" if fresh_price else "manual ⚠️",
                "currency":     currency,
                "costBasis":    cost_basis,
                "currentValue": round(current_value),
                "pl":           round(pl),
                "plPct":        pl_pct
            })

        total_pl = total_value - total_cost
        return json.dumps({
            "portfolio":         updated,
            "totalCostBasis":    round(total_cost),
            "totalCurrentValue": round(total_value),
            "totalPL":           round(total_pl),
            "totalPLPct":        round(total_pl / total_cost * 100, 1) if total_cost else 0,
            "usdToIdr":          usd_to_idr,
            "fetchedAt":         dt.datetime.now(pytz.timezone("Asia/Jakarta")).strftime("%Y-%m-%d %H:%M WIB")
        }, ensure_ascii=False)

    except ImportError:
        return json.dumps({"error": "yfinance not installed. Run: pip3 install yfinance"})
    except Exception as e:
        return json.dumps({"error": str(e)})


def exec_get_transactions(month="", category="", limit=50) -> str:
    try:
        params = {"limit": limit}
        if month:    params["month"] = month
        if category: params["category"] = category
        resp = requests.get(f"{FINANCE_URL}/api/transactions", params=params, timeout=10)
        return json.dumps(resp.json(), ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})


def exec_add_transaction(date_str, trx_type, category, account, amount, desc="") -> str:
    try:
        payload = {
            "date": date_str, "type": trx_type,
            "category": category, "account": account,
            "amount": amount, "desc": desc
        }
        resp = requests.post(f"{FINANCE_URL}/api/transactions", json=payload, timeout=10)
        result = resp.json()
        if result.get("success"):
            # Also sync data.js to GitHub
            _sync_to_github(f"trx: {date_str} {category} {account} Rp{amount:,.0f}")
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})


def exec_update_bank_balance(nick, balance) -> str:
    try:
        resp = requests.patch(f"{FINANCE_URL}/api/banks/{nick}", json={"balance": balance}, timeout=10)
        result = resp.json()
        if result.get("success"):
            _sync_to_github(f"bank: {nick} → Rp{balance:,.0f}")
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})


def _calc_ema(series, period):
    return series.ewm(span=period, adjust=False).mean()

def _calc_rsi(series, period=14):
    delta = series.diff()
    gain  = delta.clip(lower=0).rolling(period).mean()
    loss  = (-delta.clip(upper=0)).rolling(period).mean()
    rs    = gain / loss.replace(0, float('nan'))
    return 100 - (100 / (1 + rs))

def _calc_stoch(high, low, close, k_period=14, d_period=3):
    lowest_low   = low.rolling(k_period).min()
    highest_high = high.rolling(k_period).max()
    k = 100 * (close - lowest_low) / (highest_high - lowest_low).replace(0, float('nan'))
    d = k.rolling(d_period).mean()
    return k, d

def _fear_greed() -> dict:
    try:
        r = requests.get("https://api.alternative.me/fng/?limit=1", timeout=8)
        d = r.json()["data"][0]
        return {"value": int(d["value"]), "label": d["value_classification"]}
    except Exception:
        return {"value": None, "label": "unavailable"}

def exec_get_market_data(tickers: list, period: str = "3mo") -> str:
    try:
        import yfinance as yf
        results = {}

        # Fear & Greed (crypto sentiment) — fetch once
        fg = _fear_greed()

        for ticker in tickers:
            try:
                t    = yf.Ticker(ticker)
                info = t.info
                hist = t.history(period=period)

                if hist.empty:
                    results[ticker] = {"error": "no data"}
                    continue

                close  = hist["Close"]
                high   = hist["High"]
                low    = hist["Low"]
                current = round(float(close.iloc[-1]), 2)
                prev    = float(close.iloc[-2]) if len(close) > 1 else current
                change  = round((current - prev) / prev * 100, 2) if prev else 0

                # --- EMA ---
                ema9   = round(float(_calc_ema(close, 9).iloc[-1]), 2)
                ema21  = round(float(_calc_ema(close, 21).iloc[-1]), 2)
                ema50  = round(float(_calc_ema(close, 50).iloc[-1]), 2)
                ema200 = round(float(_calc_ema(close, 200).iloc[-1]), 2) if len(close) >= 200 else None
                ema_signal = "BULLISH" if current > ema21 > ema50 else ("BEARISH" if current < ema21 < ema50 else "MIXED")

                # --- RSI ---
                rsi_val  = round(float(_calc_rsi(close, 14).iloc[-1]), 1)
                if rsi_val >= 70:   rsi_signal = "OVERBOUGHT ⚠️"
                elif rsi_val <= 30: rsi_signal = "OVERSOLD ⚠️"
                else:               rsi_signal = "NEUTRAL ✅"

                # --- STOCH ---
                stoch_k, stoch_d = _calc_stoch(high, low, close)
                sk = round(float(stoch_k.iloc[-1]), 1)
                sd = round(float(stoch_d.iloc[-1]), 1)
                if sk >= 80:   stoch_signal = "OVERBOUGHT ⚠️"
                elif sk <= 20: stoch_signal = "OVERSOLD ⚠️"
                else:          stoch_signal = "NEUTRAL ✅"
                stoch_cross = "BULLISH CROSS" if sk > sd else "BEARISH CROSS"

                # --- Support / Resistance ---
                period_high = round(float(close.max()), 2)
                period_low  = round(float(close.min()), 2)
                support1    = round(period_low * 1.02, 2)
                resistance1 = round(period_high * 0.98, 2)

                results[ticker] = {
                    "name":        info.get("shortName", ticker),
                    "currency":    info.get("currency", "USD"),
                    "price":       current,
                    "change_pct":  change,
                    "period":      period,
                    # EMA
                    "ema": {
                        "ema9": ema9, "ema21": ema21, "ema50": ema50, "ema200": ema200,
                        "signal": ema_signal,
                        "note": f"Price {'above' if current > ema21 else 'below'} EMA21"
                    },
                    # RSI
                    "rsi": {
                        "value": rsi_val, "signal": rsi_signal,
                        "note": "Overbought >70, Oversold <30"
                    },
                    # STOCH
                    "stoch": {
                        "k": sk, "d": sd, "signal": stoch_signal,
                        "cross": stoch_cross,
                        "note": "Overbought >80, Oversold <20"
                    },
                    # Support/Resistance
                    "support_resistance": {
                        "support1": support1, "resistance1": resistance1,
                        "period_low": period_low, "period_high": period_high
                    },
                    # Sentiment (Fear & Greed — relevan untuk crypto)
                    "fear_greed": fg,
                    # Fundamentals
                    "market_cap":      info.get("marketCap"),
                    "52w_high":        info.get("fiftyTwoWeekHigh"),
                    "52w_low":         info.get("fiftyTwoWeekLow"),
                    "pe_ratio":        info.get("trailingPE"),
                    "avg_volume":      info.get("averageVolume"),
                }
            except Exception as ex:
                results[ticker] = {"error": str(ex)}

        return json.dumps(results, ensure_ascii=False)
    except ImportError:
        return json.dumps({"error": "yfinance not installed. Run: pip3 install yfinance"})
    except Exception as e:
        return json.dumps({"error": str(e)})


def exec_get_crypto_prices(coins: list = None) -> str:
    try:
        if not coins:
            coins = ["bitcoin", "ethereum", "solana", "binancecoin", "ripple"]
        ids = ",".join(coins)
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies=usd,idr&include_24hr_change=true&include_market_cap=true"
        resp = requests.get(url, timeout=10, headers={"accept": "application/json"})
        data = resp.json()

        result = {}
        for coin, vals in data.items():
            result[coin] = {
                "usd":          vals.get("usd"),
                "idr":          vals.get("idr"),
                "change_24h":   round(vals.get("usd_24h_change", 0), 2),
                "market_cap_usd": vals.get("usd_market_cap")
            }
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})


def exec_get_fx_rates() -> str:
    try:
        # Get IDR per 1 unit of each currency
        url = "https://api.frankfurter.app/latest?to=IDR,USD,EUR,CHF,JPY,CNY,SGD,GBP"
        resp = requests.get(url, timeout=10)
        data = resp.json()

        # Base is EUR by default, convert to IDR base
        rates_vs_eur = data.get("rates", {})
        idr_per_eur = rates_vs_eur.get("IDR", 1)

        result = {"base": "IDR", "date": data.get("date"), "rates": {}}
        for currency, rate_vs_eur in rates_vs_eur.items():
            if currency == "IDR":
                continue
            idr_per_unit = idr_per_eur / rate_vs_eur
            result["rates"][currency] = round(idr_per_unit, 2)

        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})


def exec_get_news(limit: int = 10) -> str:
    try:
        import feedparser
        feeds = [
            ("Reuters Business", "https://feeds.reuters.com/reuters/businessNews"),
            ("CNBC World",       "https://www.cnbc.com/id/100003114/device/rss/rss.html"),
            ("Bloomberg Markets","https://feeds.bloomberg.com/markets/news.rss"),
            ("Bisnis.com",       "https://ekonomi.bisnis.com/rss"),
        ]
        headlines = []
        for source, url in feeds:
            try:
                feed = feedparser.parse(url)
                for entry in feed.entries[:3]:
                    headlines.append({
                        "source":    source,
                        "title":     entry.get("title", ""),
                        "summary":   entry.get("summary", "")[:200],
                        "published": entry.get("published", ""),
                        "link":      entry.get("link", "")
                    })
                    if len(headlines) >= limit:
                        break
            except Exception:
                continue
            if len(headlines) >= limit:
                break
        return json.dumps({"headlines": headlines, "count": len(headlines)}, ensure_ascii=False)
    except ImportError:
        return json.dumps({"error": "feedparser not installed. Run: pip3 install feedparser"})
    except Exception as e:
        return json.dumps({"error": str(e)})


def _mask_acct(acct):
    """Auto-mask nomor rekening → ****XXXX (4 digit terakhir)."""
    if not acct: return acct
    acct = str(acct).strip().replace("*", "")  # strip existing asterisks
    return f"****{acct[-4:]}" if len(acct) >= 4 else acct

def exec_manage_bank(action, nick, name=None, cat=None, type_=None, acct=None, balance=None, notes=None) -> str:
    acct = _mask_acct(acct)  # always mask before saving
    try:
        if action == "create":
            payload = {"name": name, "nick": nick, "cat": cat, "type": type_, "acct": acct, "balance": balance, "notes": notes}
            resp = requests.post(f"{FINANCE_URL}/api/banks", json=payload, timeout=10)
            result = resp.json()
            # Auto-upsert: kalau UNIQUE conflict → switch ke update otomatis
            if not result.get("success") and "UNIQUE" in str(result.get("error", "")):
                update_payload = {k: v for k, v in {"name": name, "cat": cat, "type": type_, "acct": acct, "balance": balance, "notes": notes}.items() if v is not None}
                resp = requests.put(f"{FINANCE_URL}/api/banks/{nick}", json=update_payload, timeout=10)
                result = resp.json()
                result["_note"] = f"Bank '{nick}' sudah ada — data diupdate."
                action = "update"
        elif action == "update":
            payload = {k: v for k, v in {"name": name, "cat": cat, "type": type_, "acct": acct, "balance": balance, "notes": notes}.items() if v is not None}
            resp = requests.put(f"{FINANCE_URL}/api/banks/{nick}", json=payload, timeout=10)
            result = resp.json()
        elif action == "delete":
            resp = requests.delete(f"{FINANCE_URL}/api/banks/{nick}", timeout=10)
            result = resp.json()
        else:
            return json.dumps({"error": "action harus create/update/delete"})
        if result.get("success"):
            _sync_to_github(f"bank {action}: {nick}")
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})


def exec_manage_creditcard(action, name, issuer=None, limit=None, outstanding=None, due_date=None, notes=None) -> str:
    try:
        if action == "create":
            payload = {"name": name, "issuer": issuer, "limit": limit, "outstanding": outstanding, "dueDate": due_date, "notes": notes}
            resp = requests.post(f"{FINANCE_URL}/api/creditcards", json=payload, timeout=10)
        elif action == "update":
            payload = {k: v for k, v in {"issuer": issuer, "limit": limit, "outstanding": outstanding, "dueDate": due_date, "notes": notes}.items() if v is not None}
            resp = requests.put(f"{FINANCE_URL}/api/creditcards/{name}", json=payload, timeout=10)
        elif action == "delete":
            resp = requests.delete(f"{FINANCE_URL}/api/creditcards/{name}", timeout=10)
        else:
            return json.dumps({"error": "action harus create/update/delete"})
        result = resp.json()
        if result.get("success"):
            _sync_to_github(f"CC {action}: {name}")
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})


def exec_manage_investment(action, ticker, platform=None, type_=None, qty=None, avg_buy=None,
                           currency=None, cost_basis=None, current_price=None, platform_cash=None, notes=None) -> str:
    try:
        if action == "create":
            payload = {"platform": platform, "ticker": ticker, "type": type_, "qty": qty,
                       "avgBuy": avg_buy, "currency": currency, "costBasis": cost_basis,
                       "currentPrice": current_price, "platformCash": platform_cash, "notes": notes}
            resp = requests.post(f"{FINANCE_URL}/api/investments", json=payload, timeout=10)
        elif action == "update":
            payload = {k: v for k, v in {"platform": platform, "type": type_, "qty": qty, "avgBuy": avg_buy,
                       "currency": currency, "costBasis": cost_basis, "currentPrice": current_price,
                       "platformCash": platform_cash, "notes": notes}.items() if v is not None}
            resp = requests.put(f"{FINANCE_URL}/api/investments/{ticker}", json=payload, timeout=10)
        elif action == "delete":
            resp = requests.delete(f"{FINANCE_URL}/api/investments/{ticker}", timeout=10)
        else:
            return json.dumps({"error": "action harus create/update/delete"})
        result = resp.json()
        if result.get("success"):
            _sync_to_github(f"investment {action}: {ticker}")
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})


def exec_manage_loan(action, loan_type, lender=None, remaining=None, monthly=None, rate=None, tenor=None, notes=None) -> str:
    try:
        if action == "create":
            payload = {"type": loan_type, "lender": lender, "remaining": remaining,
                       "monthly": monthly, "rate": rate, "tenor": tenor, "notes": notes}
            resp = requests.post(f"{FINANCE_URL}/api/loans", json=payload, timeout=10)
        elif action == "update":
            payload = {k: v for k, v in {"lender": lender, "remaining": remaining, "monthly": monthly,
                       "rate": rate, "tenor": tenor, "notes": notes}.items() if v is not None}
            resp = requests.put(f"{FINANCE_URL}/api/loans/{loan_type}", json=payload, timeout=10)
        elif action == "delete":
            resp = requests.delete(f"{FINANCE_URL}/api/loans/{loan_type}", timeout=10)
        else:
            return json.dumps({"error": "action harus create/update/delete"})
        result = resp.json()
        if result.get("success"):
            _sync_to_github(f"loan {action}: {loan_type}")
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})


def exec_manage_budget(action, category, amount=None) -> str:
    try:
        if action in ("create", "update"):
            if amount is None:
                return json.dumps({"error": "amount wajib untuk create/update"})
            resp = requests.patch(f"{FINANCE_URL}/api/budgets", json={"budgets": {category: amount}}, timeout=10)
        elif action == "delete":
            resp = requests.delete(f"{FINANCE_URL}/api/budgets/{category}", timeout=10)
        else:
            return json.dumps({"error": "action harus create/update/delete"})
        result = resp.json()
        if result.get("success"):
            _sync_to_github(f"budget {action}: {category}")
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})


def exec_manage_transaction(action, trx_id, date_str=None, type_=None, category=None, account=None, amount=None, desc=None) -> str:
    try:
        if action == "update":
            payload = {k: v for k, v in {"date": date_str, "type": type_, "category": category,
                       "account": account, "amount": amount, "desc": desc}.items() if v is not None}
            resp = requests.put(f"{FINANCE_URL}/api/transactions/{trx_id}", json=payload, timeout=10)
        elif action == "delete":
            resp = requests.delete(f"{FINANCE_URL}/api/transactions/{trx_id}", timeout=10)
        else:
            return json.dumps({"error": "action harus update/delete"})
        result = resp.json()
        if result.get("success"):
            _sync_to_github(f"trx {action}: {trx_id}")
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})


def _sync_to_github(commit_msg: str):
    """Regenerate data.js from API and push to GitHub."""
    try:
        # Fetch full data from API
        resp = requests.get(f"{FINANCE_URL}/api/data", timeout=10)
        api_data = resp.json()

        # Read current data.js to preserve structure
        data_js_path = PROJECT_ROOT / "data.js"
        if not data_js_path.exists():
            logger.warning("data.js not found, skipping GitHub sync")
            return

        # Write updated data.js
        js_content = f"""// data.js — Auto-synced from Finance API
// Last updated: {dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
// DO NOT EDIT MANUALLY — managed by Edith

const FINANCE_DATA = {json.dumps(api_data, ensure_ascii=False, indent=2)};

if (typeof window !== 'undefined') {{
  window.EDITH_API_DATA = FINANCE_DATA;
}}
"""
        data_js_path.write_text(js_content, encoding="utf-8")

        # Git push — set HOME/PATH eksplisit biar launchctl punya credentials
        _env = {
            **os.environ,
            "HOME": str(_Path.home()),
            "PATH": "/usr/local/bin:/usr/bin:/bin:/opt/homebrew/bin",
            "GIT_SSH_COMMAND": "ssh -o StrictHostKeyChecking=no"
        }
        # Remove stale lock if exists
        lock = PROJECT_ROOT / ".git" / "index.lock"
        if lock.exists(): lock.unlink()

        subprocess.run(["git", "add", "data.js"], cwd=PROJECT_ROOT, check=True, capture_output=True, env=_env)
        result = subprocess.run(
            ["git", "commit", "-m", f"[Edith] {commit_msg}"],
            cwd=PROJECT_ROOT, capture_output=True, env=_env
        )
        if result.returncode not in (0, 1):  # 1 = nothing to commit, ok
            raise Exception(result.stderr.decode())
        subprocess.run(["git", "push"], cwd=PROJECT_ROOT, check=True, capture_output=True, env=_env)
        logger.info(f"✅ GitHub synced: {commit_msg}")
    except Exception as e:
        logger.warning(f"⚠️ GitHub sync failed (non-critical): {e}")


# ============================================================
# ERROR CONTEXT ENRICHER
# ============================================================
def _enrich_error(result: str, tool_name: str, args: dict) -> str:
    """
    Kalau tool return error, tambahkan konteks human-readable
    supaya Edith bisa jelaskan ke user dengan benar.
    """
    try:
        data = json.loads(result)
        if "error" not in data:
            return result
        err = str(data["error"]).lower()

        # Determine friendly context
        if "connection" in err or "refused" in err or "econnrefused" in err:
            context = "Server finance (localhost:3000) tidak bisa dihubungi"
            solution = "Jalankan `node backend/server.js` dari Terminal"
        elif "404" in err or "not found" in err:
            entity = tool_name.replace("exec_manage_", "").replace("exec_get_", "")
            key = args.get("nick") or args.get("name") or args.get("id") or args.get("ticker") or args.get("loanType") or args.get("category") or "?"
            context = f"Data '{key}' tidak ditemukan di database"
            if "bank" in tool_name:
                solution = "Cek nama rekening yang terdaftar dengan: 'rekening gua apa aja?'"
            elif "transaction" in tool_name:
                solution = "Minta histori transaksi dulu untuk lihat ID yang valid: 'histori transaksi gua'"
            elif "creditcard" in tool_name or "cc" in tool_name:
                solution = "Cek CC yang terdaftar: 'CC gua apa aja?'"
            elif "investment" in tool_name:
                solution = "Cek investasi terdaftar: 'portfolio gua'"
            else:
                solution = f"Pastikan data '{key}' sudah ada sebelum di-edit/hapus"
        elif "400" in err or "invalid" in err or "required" in err:
            context = "Data yang dikirim tidak valid atau tidak lengkap"
            solution = "Cek: tanggal harus YYYY-MM-DD, amount harus angka, field wajib tidak boleh kosong"
        elif "yfinance" in err or "no data" in err or "no timezone" in err:
            ticker = args.get("tickers", ["?"])[0] if isinstance(args.get("tickers"), list) else "?"
            context = f"Data market untuk '{ticker}' tidak tersedia"
            solution = "Coba ticker yang berbeda atau cek koneksi internet"
        elif "rate limit" in err or "429" in err:
            context = "API rate limit tercapai"
            solution = "Tunggu 30-60 detik lalu coba lagi"
        elif "timeout" in err:
            context = "Request timeout — koneksi lambat atau server tidak responsif"
            solution = "Coba lagi dalam beberapa detik"
        else:
            context = f"Error teknis pada {tool_name}"
            solution = "Coba lagi atau cek apakah server dan koneksi internet berjalan normal"

        data["_error_context"] = {
            "tool": tool_name,
            "context": context,
            "solution": solution
        }
        return json.dumps(data, ensure_ascii=False)
    except Exception:
        return result


# ============================================================
# TOOL DISPATCHER
# ============================================================
def execute_tool(name: str, args: dict) -> str:
    logger.info(f"🔧 {name}({args})")

    if name == "get_banks":
        result = exec_get_banks()
    elif name == "get_credit_cards":
        result = exec_get_credit_cards()
    elif name == "get_investments":
        result = exec_get_investments()
    elif name == "get_loans":
        result = exec_get_loans()
    elif name == "get_budgets":
        result = exec_get_budgets()
    elif name == "get_expenses":
        result = exec_get_expenses(month=args.get("month", ""))
    elif name == "get_income":
        result = exec_get_income(month=args.get("month", ""))
    elif name == "get_summary":
        result = exec_get_summary()
    elif name == "get_receivables":
        result = exec_get_receivables()
    elif name == "get_fixed_assets":
        result = exec_get_fixed_assets()
    elif name == "get_expenses_compare":
        result = exec_get_expenses_compare(month1=args.get("month1",""), month2=args.get("month2",""))
    elif name == "get_investment_pl":
        result = exec_get_investment_pl()
    elif name == "get_transactions":
        result = exec_get_transactions(
            month=args.get("month", ""),
            category=args.get("category", ""),
            limit=args.get("limit", 50)
        )
    elif name == "add_transaction":
        result = exec_add_transaction(
            date_str=_date(args.get("date")),
            trx_type=args.get("type", "Out"),
            category=args.get("category", ""),
            account=args.get("account", ""),
            amount=_num(args.get("amount"), 0),
            desc=args.get("desc", "")
        )
    elif name == "update_bank_balance":
        result = exec_update_bank_balance(
            nick=args.get("nick", ""),
            balance=_num(args.get("balance"), 0)
        )
    elif name == "get_market_data":
        result = exec_get_market_data(
            tickers=args.get("tickers", ["^JKSE", "^GSPC"]),
            period=args.get("period", "3mo")
        )
    elif name == "get_crypto_prices":
        result = exec_get_crypto_prices(coins=args.get("coins"))
    elif name == "get_fx_rates":
        result = exec_get_fx_rates()
    elif name == "get_news":
        result = exec_get_news(limit=args.get("limit", 10))
    elif name == "manage_bank":
        result = exec_manage_bank(
            action=args.get("action"), nick=args.get("nick"),
            name=args.get("name"), cat=args.get("cat"), type_=args.get("type"),
            acct=args.get("acct"), balance=args.get("balance"), notes=args.get("notes")
        )
    elif name == "manage_creditcard":
        result = exec_manage_creditcard(
            action=args.get("action"), name=args.get("name"),
            issuer=args.get("issuer"),
            limit=_num(args.get("limit")) if args.get("limit") is not None else None,
            outstanding=_num(args.get("outstanding")) if args.get("outstanding") is not None else None,
            due_date=args.get("dueDate"),
            notes=args.get("notes")
        )
    elif name == "manage_investment":
        result = exec_manage_investment(
            action=args.get("action"), ticker=args.get("ticker"),
            platform=args.get("platform"), type_=args.get("type"),
            qty=args.get("qty"), avg_buy=args.get("avgBuy"),
            currency=args.get("currency"), cost_basis=args.get("costBasis"),
            current_price=args.get("currentPrice"), platform_cash=args.get("platformCash"),
            notes=args.get("notes")
        )
    elif name == "manage_loan":
        result = exec_manage_loan(
            action=args.get("action"), loan_type=args.get("loanType"),
            lender=args.get("lender"), remaining=args.get("remaining"),
            monthly=args.get("monthly"), rate=args.get("rate"),
            tenor=args.get("tenor"), notes=args.get("notes")
        )
    elif name == "manage_budget":
        result = exec_manage_budget(
            action=args.get("action"), category=args.get("category"),
            amount=_num(args.get("amount")) if args.get("amount") is not None else None
        )
    elif name == "manage_transaction":
        result = exec_manage_transaction(
            action=args.get("action"), trx_id=args.get("id"),
            date_str=_date(args.get("date")) if args.get("date") else None,
            type_=args.get("type"),
            category=args.get("category"), account=args.get("account"),
            amount=_num(args.get("amount")) if args.get("amount") is not None else None,
            desc=args.get("desc")
        )
    elif name == "save_memory":
        _save_memory_entry(args.get("key", ""), args.get("value", ""))
        result = json.dumps({"success": True, "saved": args.get("key")})
        logger.info(f"🧠 Memory saved: {args.get('key')} = {args.get('value')[:60]}")
    elif name == "get_memory":
        mem = _load_memory()
        result = json.dumps({"memory": mem, "count": len(mem)}, ensure_ascii=False)
    else:
        result = json.dumps({"error": f"Tool '{name}' tidak dikenal. Ini bug — laporkan ke developer."})

    # Semua hasil dilewatkan ke error enricher → friendly context kalau ada error
    return _enrich_error(result, name, args)

# ============================================================
# GROQ AGENTIC LOOP (OpenAI-compatible)
# ============================================================
def chat_with_groq(messages: list, model: str = MODEL_FAST, tools: list = None) -> str:
    if not GROQ_API_KEY:
        return "❌ GROQ_API_KEY belum diset. Tambahkan ke backend/.env"

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    current = messages.copy()
    active_tools = tools if tools else TOOL_GROUPS.get("summary", TOOLS)
    # 8B tidak reliable untuk write tool calling → upgrade ke 70B kalau ada write tools
    _write_names = set(_WRITE_CORE)
    _active_tool_names = {t["function"]["name"] for t in active_tools}
    if model == MODEL_FAST and _active_tool_names & _write_names:
        model = MODEL_SMART
        logger.info("⬆️ Auto-upgrade ke 70B (write tools present)")
    # Fallback: if 70B hits rate limit, retry with 8B
    models_to_try = [model] if model == MODEL_FAST else [model, MODEL_FAST]

    _executed_writes: set = set()  # dedup: cegah model re-execute write op yang sama

    for iteration in range(6):  # max 6 iterations
        payload = {
            "model":       models_to_try[0],
            "messages":    current,
            "tools":       active_tools,
            "tool_choice": "auto",
            "temperature": 0.3,
            "max_tokens":  1024
        }
        resp = requests.post(GROQ_URL, json=payload, headers=headers, timeout=60)
        # 429 rate limit → fallback ke model lebih kecil
        if resp.status_code == 429 and len(models_to_try) > 1:
            logger.warning(f"⚠️ 429 rate limit on {models_to_try[0]}, fallback ke {models_to_try[1]}")
            models_to_try = [models_to_try[1]]
            payload["model"] = models_to_try[0]
            resp = requests.post(GROQ_URL, json=payload, headers=headers, timeout=60)
        if not resp.ok:
            logger.error(f"❌ Groq {resp.status_code}: {resp.text[:500]}")
            # 400 tool_use_failed → auto-retry dengan 70B + clean history
            if resp.status_code == 400 and "tool_use_failed" in resp.text:
                if models_to_try[0] != MODEL_SMART:
                    logger.warning("🔄 400 tool_use_failed → retry dengan 70B")
                    models_to_try = [MODEL_SMART]
                    continue
                elif iteration == 0:
                    # Sudah 70B tapi masih 400 → strip tool_calls dari history, retry tanpa tools
                    logger.warning("🔄 400 pada 70B → retry tanpa tools")
                    current = [m for m in current if m.get("role") != "tool" and "tool_calls" not in m]
                    active_tools = []
                    continue
            resp.raise_for_status()
        data    = resp.json()
        choice  = data["choices"][0]
        message = choice["message"]
        content    = message.get("content") or ""
        tool_calls = message.get("tool_calls") or []

        if not tool_calls:
            return content or "Maaf, ga ada respons."

        # Append assistant message (with tool_calls intact)
        current.append({
            "role":       "assistant",
            "content":    content,
            "tool_calls": tool_calls
        })

        # Execute each tool call
        for tc in tool_calls:
            fn   = tc.get("function", {})
            name = fn.get("name", "")
            args = fn.get("arguments", {})
            if isinstance(args, str):
                try: args = json.loads(args)
                except: args = {}
            # Dedup write ops — skip kalau exact same call sudah dieksekusi di loop ini
            if name in _WRITE_CORE:
                dedup_key = f"{name}:{json.dumps(args, sort_keys=True)}"
                if dedup_key in _executed_writes:
                    logger.warning(f"⏭️ Skip duplicate write: {name}")
                    result = json.dumps({"success": True, "_note": "skipped duplicate"})
                    current.append({"role": "tool", "tool_call_id": tc.get("id", ""), "content": result})
                    continue
                _executed_writes.add(dedup_key)
            result = execute_tool(name, args)
            # Truncate large results to avoid 413 Payload Too Large
            if len(result) > MAX_TOOL_RESULT:
                result = result[:MAX_TOOL_RESULT] + "\n...[truncated]"
            logger.info(f"✅ Tool result: {result[:120]}...")
            # OpenAI format requires tool_call_id
            current.append({
                "role":         "tool",
                "tool_call_id": tc.get("id", ""),
                "content":      result
            })

    return "Maaf, terlalu banyak iterasi tool call."

# ============================================================
# CONVERSATION HISTORY & SUBSCRIBERS
# ============================================================
histories:   dict = {}
subscribers: dict = {}  # uid -> chat_id

def get_history(uid: int) -> list:
    return histories.setdefault(uid, [])

def add_msg(uid: int, role: str, content: str):
    h = get_history(uid)
    h.append({"role": role, "content": content})
    if len(h) > MAX_HISTORY:
        histories[uid] = h[-MAX_HISTORY:]

def clear_history(uid: int):
    histories[uid] = []

# ============================================================
# DAILY BRIEF HELPERS
# ============================================================
def _fetch_news_by_region():
    """Fetch news, split national (ID) vs international."""
    try:
        import feedparser
        national_feeds = [
            ("Bisnis.com",    "https://ekonomi.bisnis.com/rss"),
            ("CNBC Indonesia","https://www.cnbcindonesia.com/rss"),
            ("Kontan",        "https://rss.kontan.co.id/"),
        ]
        intl_feeds = [
            ("Reuters",   "https://feeds.reuters.com/reuters/businessNews"),
            ("CNBC World","https://www.cnbc.com/id/100003114/device/rss/rss.html"),
            ("Bloomberg", "https://feeds.bloomberg.com/markets/news.rss"),
        ]
        def scrape(feeds, limit=3):
            items = []
            for source, url in feeds:
                try:
                    feed = feedparser.parse(url)
                    for e in feed.entries[:2]:
                        items.append({
                            "source":  source,
                            "title":   e.get("title", "").strip(),
                            "link":    e.get("link", ""),
                            "summary": e.get("summary", "")[:150].strip()
                        })
                        if len(items) >= limit: break
                except Exception: continue
                if len(items) >= limit: break
            return items[:limit]
        return scrape(national_feeds, 3), scrape(intl_feeds, 3)
    except Exception as e:
        return [], []

def _fmt_ta_mini(d: dict) -> str:
    """One-line TA summary for daily brief."""
    if not d or "error" in d: return "N/A"
    rsi  = d.get("rsi", {})
    stch = d.get("stoch", {})
    ema  = d.get("ema", {})
    fg   = d.get("fear_greed", {})
    parts = []
    if rsi.get("value"):  parts.append(f"RSI {rsi['value']}")
    if stch.get("k"):     parts.append(f"Stoch K{stch['k']}")
    if ema.get("signal"): parts.append(ema["signal"])
    if fg.get("value"):   parts.append(f"F&G {fg['value']} {fg.get('label','')}")
    return " | ".join(parts) if parts else "N/A"


# ============================================================
# DAILY BRIEF — 2 CHAT MESSAGES
# ============================================================
async def send_daily_brief(context: ContextTypes.DEFAULT_TYPE):
    """Auto-send morning brief ke semua subscriber — 2 pesan terpisah."""
    if not subscribers:
        return

    today = dt.datetime.now(pytz.timezone("Asia/Jakarta")).strftime("%d %b %Y")

    try:
        # --- Fetch semua data ---
        markets = json.loads(exec_get_market_data(
            ["^JKSE", "^GSPC", "BTC-USD", "ETH-USD", "SOL-USD", "SPY", "EIDO"], "5d"
        ))
        fx      = json.loads(exec_get_fx_rates())
        news_id, news_intl = _fetch_news_by_region()
        fin     = json.loads(exec_get_finance_data())

        # ── CHAT 1: NEWS + MARKET ──────────────────────────────
        def fmt_asset(ticker, label):
            d = markets.get(ticker, {})
            if not d or "error" in d: return f"• {label}: N/A"
            chg   = d.get("change_pct", 0)
            price = d.get("price", 0)
            emoji = "🟢" if chg >= 0 else "🔴"
            ta    = _fmt_ta_mini(d)
            cur   = d.get("currency", "")
            p_fmt = f"${price:,.2f}" if cur == "USD" else f"{price:,.2f}"
            return f"• {label}: {p_fmt} {emoji}{chg:+.2f}%\n  _{ta}_"

        fx_rates = fx.get("rates", {})
        def fmt_fx(c): return f"Rp{fx_rates.get(c,0):,.0f}" if c in fx_rates else "N/A"

        # News blocks
        def fmt_news(items):
            lines = []
            for i, n in enumerate(items, 1):
                link = f" [→]({n['link']})" if n.get("link") else ""
                lines.append(f"{i}\\. *{n['title'][:80]}*{link}\n   _{n['source']}_")
            return "\n".join(lines) if lines else "_Tidak ada berita_"

        chat1 = (
            f"🌅 *Edith Morning Brief — {today}*\n"
            f"\n🇮🇩 *News Nasional*\n{fmt_news(news_id)}"
            f"\n\n🌐 *News Internasional*\n{fmt_news(news_intl)}"
            f"\n\n📈 *Market Update*\n"
            f"{fmt_asset('^JKSE',  'IHSG')}\n"
            f"{fmt_asset('^GSPC',  'S&P 500')}\n"
            f"{fmt_asset('SPY',    'SPY ETF')}\n"
            f"{fmt_asset('EIDO',   'EIDO ETF')}\n"
            f"{fmt_asset('BTC-USD','BTC')}\n"
            f"{fmt_asset('ETH-USD','ETH')}\n"
            f"{fmt_asset('SOL-USD','SOL')}"
            f"\n\n💱 *FX*: USD {fmt_fx('USD')} | EUR {fmt_fx('EUR')} | SGD {fmt_fx('SGD')}"
        )

        # ── CHAT 2: SALDO BANK + BUDGET ALERT ─────────────────
        banks   = fin.get("banks", [])
        budgets = fin.get("budgets", {})
        trx_now = fin.get("transactionsThisMonth", [])

        # Hitung spending per kategori bulan ini
        spending: dict = {}
        for t in trx_now:
            if t.get("type") == "Out":
                cat = t.get("category", "Other")
                spending[cat] = spending.get(cat, 0) + t.get("amount", 0)

        # Over-budget alerts
        alerts = []
        for cat, budget_amt in budgets.items():
            if budget_amt > 0:
                spent = spending.get(cat, 0)
                pct   = spent / budget_amt * 100
                if pct >= 80:
                    status = "🔴 OVER" if pct >= 100 else "⚠️ 80%+"
                    alerts.append(f"{status} {cat}: Rp{spent:,.0f} / Rp{budget_amt:,.0f} ({pct:.0f}%)")

        bank_lines = "\n".join(
            f"• {b['nick']}: *Rp{b['balance']:,.0f}*" + (f" _{b.get('notes','')[:40]}_" if b.get("notes") else "")
            for b in banks
        )
        total_bank = sum(b.get("balance", 0) for b in banks)

        alert_block = (
            "\n\n⚠️ *Budget Alert*\n" + "\n".join(alerts)
            if alerts else "\n\n✅ *Semua kategori masih dalam budget*"
        )

        chat2 = (
            f"💰 *Saldo Bank — {today}*\n\n"
            f"{bank_lines}\n\n"
            f"*Total Cash: Rp{total_bank:,.0f}*"
            f"{alert_block}"
        )

        # --- Kirim 2 pesan ---
        for uid, chat_id in subscribers.items():
            try:
                await context.bot.send_message(chat_id=chat_id, text=chat1,
                                               parse_mode="MarkdownV2", disable_web_page_preview=True)
                await context.bot.send_message(chat_id=chat_id, text=chat2,
                                               parse_mode="Markdown")
            except Exception as e:
                logger.error(f"Failed to send brief to {uid}: {e}")

    except Exception as e:
        logger.error(f"Daily brief error: {e}")

# ============================================================
# TELEGRAM HANDLERS
# ============================================================
logging.basicConfig(format="%(asctime)s [%(levelname)s] %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)


async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    name = update.effective_user.first_name
    logger.info(f"📱 /start — User: {name} | ID: {uid}")
    await update.message.reply_text(
        f"Hei {name}! Gua Edith 💼\n\n"
        f"*User ID lo: `{uid}`*\n\n"
        f"Yang bisa gua lakuin:\n"
        f"• Catat transaksi\n"
        f"• Analisis keuangan & net worth\n"
        f"• Update saldo bank\n"
        f"• Cek saham (IDX & global)\n"
        f"• Analisis crypto\n"
        f"• FX rates & IHSG/SPX\n"
        f"• Resume news pasar\n\n"
        f"Commands:\n"
        f"/clear — reset conversation\n"
        f"/status — cek koneksi\n"
        f"/subscribe — daily brief tiap pagi\n"
        f"/unsubscribe — stop daily brief",
        parse_mode="Markdown"
    )


async def cmd_clear(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    clear_history(update.effective_user.id)
    await update.message.reply_text("✅ Conversation reset.")


async def cmd_status(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    lines = []
    # Finance API
    try:
        r = requests.get(f"{FINANCE_URL}/api/health", timeout=5)
        d = r.json()
        lines.append(f"✅ Finance API — {d.get('transactions', '?')} transaksi")
    except Exception as e:
        lines.append(f"❌ Finance API — {e}")
    # Groq API
    try:
        r = requests.get(
            "https://api.groq.com/openai/v1/models",
            headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
            timeout=5
        )
        if r.status_code == 200:
            lines.append(f"✅ Groq API — connected")
            lines.append(f"   Fast  : {MODEL_FAST}")
            lines.append(f"   Smart : {MODEL_SMART}")
        else:
            lines.append(f"⚠️ Groq API — HTTP {r.status_code}")
    except Exception as e:
        lines.append(f"❌ Groq API — {e}")
    # Data sources
    try:
        requests.get("https://api.frankfurter.app/latest", timeout=5)
        lines.append("✅ FX API (frankfurter.app)")
    except:
        lines.append("❌ FX API")
    try:
        requests.get("https://api.coingecko.com/api/v3/ping", timeout=5)
        lines.append("✅ CoinGecko API")
    except:
        lines.append("❌ CoinGecko")

    lines.append(f"\n📊 Subscribers daily brief: {len(subscribers)}")
    await update.message.reply_text("\n".join(lines))


async def cmd_subscribe(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid     = update.effective_user.id
    chat_id = update.effective_chat.id
    subscribers[uid] = chat_id
    await update.message.reply_text(
        f"✅ Subscribe daily brief aktif!\n"
        f"Tiap pagi jam 05:00 WIB lo dapat 2 pesan:\n"
        f"1️⃣ Hot news + market update (IHSG, SPX, BTC, ETH, SOL, ETF) + TA indicators\n"
        f"2️⃣ Snapshot saldo semua bank + budget alert"
    )


async def cmd_unsubscribe(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    subscribers.pop(uid, None)
    await update.message.reply_text("✅ Unsubscribed dari daily brief.")


async def handle_message(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    uid  = user.id
    text = update.message.text

    if ALLOWED_USER_IDS and uid not in ALLOWED_USER_IDS:
        logger.warning(f"Blocked: {uid}")
        return

    logger.info(f"💬 [{uid}] {user.first_name}: {text}")

    add_msg(uid, "user", text)
    messages = [{"role": "system", "content": build_system_prompt()}] + get_history(uid)

    # Send placeholder immediately so user knows bot received it
    placeholder = await update.message.reply_text("⏳")

    try:
        # Keep sending typing action every 4s while processing
        import asyncio

        async def keep_typing():
            while True:
                await ctx.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
                await asyncio.sleep(4)

        typing_task = asyncio.create_task(keep_typing())
        try:
            model, tools = route(text, get_history(uid))
            logger.info(f"🧠 Model: {model} | Tools: {[t['function']['name'] for t in tools]}")
            response = await asyncio.get_event_loop().run_in_executor(
                None, chat_with_groq, messages, model, tools
            )
        finally:
            typing_task.cancel()

        add_msg(uid, "assistant", response)

        # Edit placeholder with real response — plain text, no parse_mode
        try:
            await placeholder.edit_text(response)
        except Exception as e:
            logger.error(f"edit_text error: {e}")
            await placeholder.edit_text(str(response)[:4000])

    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        await placeholder.edit_text(f"❌ Error: {e}\n\nCoba /status untuk cek koneksi.")


# ============================================================
# MAIN
# ============================================================
def main():
    if "PASTE_BOT_TOKEN" in BOT_TOKEN:
        print("❌ Set BOT_TOKEN dulu!")
        return

    logger.info("🚀 Edith Telegram Bot v2 starting...")
    logger.info(f"   Fast model : {MODEL_FAST}")
    logger.info(f"   Smart model: {MODEL_SMART}")
    logger.info(f"   Finance API: {FINANCE_URL}")
    logger.info(f"   Groq key   : {'✅ set' if GROQ_API_KEY else '❌ MISSING — set GROQ_API_KEY in .env'}")

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start",       cmd_start))
    app.add_handler(CommandHandler("clear",       cmd_clear))
    app.add_handler(CommandHandler("status",      cmd_status))
    app.add_handler(CommandHandler("subscribe",   cmd_subscribe))
    app.add_handler(CommandHandler("unsubscribe", cmd_unsubscribe))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Daily brief — pakai built-in job_queue (no event loop issue)
    wib = pytz.timezone("Asia/Jakarta")
    app.job_queue.run_daily(
        send_daily_brief,
        time=dt.time(hour=5, minute=0, tzinfo=wib),
        name="daily_brief"
    )
    logger.info("⏰ Daily brief scheduled at 05:00 WIB")

    logger.info("✅ Bot running. Ctrl+C to stop.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
