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
import datetime as dt
from datetime import date
from pathlib import Path
import pytz
from telegram import Update, constants
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ============================================================
# CONFIG
# ============================================================
BOT_TOKEN    = os.getenv("TELEGRAM_BOT_TOKEN", "8271171170:AAEjzBhJ1PX02mLSaP9lC7ZG18wJtzoERZQ")
OLLAMA_URL   = "http://localhost:11434/api/chat"
FINANCE_URL  = "http://localhost:3000"
MODEL        = "qwen3:latest"
PROJECT_ROOT = Path(__file__).parent.parent

# Whitelist: kosong = semua bisa akses. Isi setelah dapat user ID dari /start log.
ALLOWED_USER_IDS = []

# Daily brief jam 7 pagi WIB (UTC+7 = UTC 00:00)
DAILY_BRIEF_HOUR_UTC = 0

MAX_HISTORY = 20

# ============================================================
# SYSTEM PROMPT
# ============================================================
SYSTEM_PROMPT = """You are Edith, a personal finance and market intelligence AI assistant.

## Finance Rules
- ALWAYS call get_finance_data before answering about balances, net worth, expenses, or financial health
- Call get_transactions when user asks about spending details or transaction history
- Call add_transaction when user wants to record a new transaction
- Call update_bank_balance when user wants to update a bank balance
- Numbers: Rp 15,000,000 format (not 15000000)
- Lead with number/insight, then explain. Short & direct.
- Flag risks ⚠️, positives ✅
- Tables when comparing multiple items

## Market Rules
- Call get_market_data for stock/IHSG/SPX/ETF questions
- Call get_crypto_prices for crypto questions
- Call get_fx_rates for currency/FX questions
- Call get_news for market news or exposure analysis
- For technical analysis: mention support/resistance levels when data available
- Always state data is for information only, not financial advice

## Key Metrics
- Net Worth = Total Assets − Total Liabilities
- DTI = Monthly Installments ÷ Net Monthly Income (alert >30%)
- CC Utilization = Outstanding ÷ Limit (alert >70%)
- Cash Flow = Income − (Cash Expenses + CC Usage)

## Language
Match user's language naturally (Indonesian/English/mixed Jaksel style is fine)"""

# ============================================================
# TOOLS DEFINITION (Ollama / OpenAI format)
# ============================================================
TOOLS = [
    # --- Finance ---
    {
        "type": "function",
        "function": {
            "name": "get_finance_data",
            "description": "Ambil snapshot keuangan lengkap: saldo bank, CC, pinjaman, investasi, aset tetap, piutang, budget, dan transaksi bulan ini. Wajib dipanggil sebelum menjawab pertanyaan keuangan.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_transactions",
            "description": "Ambil histori transaksi dengan filter opsional.",
            "parameters": {
                "type": "object",
                "properties": {
                    "month":    {"type": "string",  "description": "Format YYYY-MM, e.g. 2026-06"},
                    "category": {"type": "string",  "description": "Nama kategori, e.g. Meals, Transportation"},
                    "limit":    {"type": "integer", "description": "Max transaksi (default 50)"}
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
                        "description": "List ticker. IDX: BBCA.JK, TLKM.JK. Global: AAPL, MSFT. Index: ^JKSE, ^GSPC. ETF: SPY, EIDO."
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
                    "type":         {"type": "string", "description": "Tipe: Saham IDX / ETF / Crypto / Reksadana"},
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
    }
]

# ============================================================
# TOOL EXECUTORS
# ============================================================

def exec_get_finance_data() -> str:
    try:
        resp = requests.get(f"{FINANCE_URL}/api/data", timeout=10)
        raw = resp.json()
        today = dt.datetime.now().strftime("%Y-%m")
        monthly_trx = [t for t in raw.get("transactions", []) if t.get("date", "").startswith(today)]
        summary = {
            "lastUpdated": raw.get("lastUpdated"),
            "fxRate": raw.get("fxRate"),
            "banks": raw.get("banks", []),
            "creditCards": raw.get("creditCards", []),
            "loans": raw.get("loans", []),
            "investments": raw.get("investments", []),
            "fixedAssets": raw.get("fixedAssets", []),
            "receivables": raw.get("receivables", []),
            "budgets": raw.get("budgets", {}),
            "income": raw.get("income", {}),
            "transactionsThisMonth": monthly_trx,
            "totalTransactions": len(raw.get("transactions", []))
        }
        return json.dumps(summary, ensure_ascii=False)
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


def exec_get_market_data(tickers: list, period: str = "3mo") -> str:
    try:
        import yfinance as yf
        results = {}
        for ticker in tickers:
            try:
                t = yf.Ticker(ticker)
                info = t.info
                hist = t.history(period=period)

                if hist.empty:
                    results[ticker] = {"error": "no data"}
                    continue

                current = hist["Close"].iloc[-1]
                prev    = hist["Close"].iloc[-2] if len(hist) > 1 else current
                change  = ((current - prev) / prev * 100) if prev else 0

                # Simple support/resistance (52w)
                high52 = hist["Close"].max()
                low52  = hist["Close"].min()

                results[ticker] = {
                    "price":       round(current, 2),
                    "change_pct":  round(change, 2),
                    "high_period": round(high52, 2),
                    "low_period":  round(low52, 2),
                    "support_est": round(low52 * 1.02, 2),   # ~2% above period low
                    "resistance_est": round(high52 * 0.98, 2),
                    "currency":    info.get("currency", ""),
                    "name":        info.get("shortName", ticker),
                    "sector":      info.get("sector", ""),
                    "pe_ratio":    info.get("trailingPE"),
                    "pb_ratio":    info.get("priceToBook"),
                    "market_cap":  info.get("marketCap"),
                    "dividend_yield": info.get("dividendYield"),
                    "52w_high":    info.get("fiftyTwoWeekHigh"),
                    "52w_low":     info.get("fiftyTwoWeekLow"),
                    "avg_volume":  info.get("averageVolume"),
                    "period":      period
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


def exec_manage_bank(action, nick, name=None, cat=None, type_=None, acct=None, balance=None, notes=None) -> str:
    try:
        if action == "create":
            payload = {"name": name, "nick": nick, "cat": cat, "type": type_, "acct": acct, "balance": balance, "notes": notes}
            resp = requests.post(f"{FINANCE_URL}/api/banks", json=payload, timeout=10)
        elif action == "update":
            payload = {k: v for k, v in {"name": name, "cat": cat, "type": type_, "acct": acct, "balance": balance, "notes": notes}.items() if v is not None}
            resp = requests.put(f"{FINANCE_URL}/api/banks/{nick}", json=payload, timeout=10)
        elif action == "delete":
            resp = requests.delete(f"{FINANCE_URL}/api/banks/{nick}", timeout=10)
        else:
            return json.dumps({"error": "action harus create/update/delete"})
        result = resp.json()
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

        # Git push
        subprocess.run(["git", "add", "data.js"], cwd=PROJECT_ROOT, check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", f"[Edith] {commit_msg}"],
            cwd=PROJECT_ROOT, check=True, capture_output=True
        )
        subprocess.run(["git", "push"], cwd=PROJECT_ROOT, check=True, capture_output=True)
        logger.info(f"✅ GitHub synced: {commit_msg}")
    except Exception as e:
        logger.warning(f"⚠️ GitHub sync failed (non-critical): {e}")


# ============================================================
# TOOL DISPATCHER
# ============================================================
def execute_tool(name: str, args: dict) -> str:
    logger.info(f"🔧 {name}({args})")
    if name == "get_finance_data":
        return exec_get_finance_data()
    elif name == "get_transactions":
        return exec_get_transactions(
            month=args.get("month", ""),
            category=args.get("category", ""),
            limit=args.get("limit", 50)
        )
    elif name == "add_transaction":
        return exec_add_transaction(
            date_str=args.get("date", date.today().isoformat()),
            trx_type=args.get("type", "Out"),
            category=args.get("category", ""),
            account=args.get("account", ""),
            amount=args.get("amount", 0),
            desc=args.get("desc", "")
        )
    elif name == "update_bank_balance":
        return exec_update_bank_balance(
            nick=args.get("nick", ""),
            balance=args.get("balance", 0)
        )
    elif name == "get_market_data":
        return exec_get_market_data(
            tickers=args.get("tickers", ["^JKSE", "^GSPC"]),
            period=args.get("period", "3mo")
        )
    elif name == "get_crypto_prices":
        return exec_get_crypto_prices(coins=args.get("coins"))
    elif name == "get_fx_rates":
        return exec_get_fx_rates()
    elif name == "get_news":
        return exec_get_news(limit=args.get("limit", 10))
    elif name == "manage_bank":
        return exec_manage_bank(
            action=args.get("action"), nick=args.get("nick"),
            name=args.get("name"), cat=args.get("cat"), type_=args.get("type"),
            acct=args.get("acct"), balance=args.get("balance"), notes=args.get("notes")
        )
    elif name == "manage_creditcard":
        return exec_manage_creditcard(
            action=args.get("action"), name=args.get("name"),
            issuer=args.get("issuer"), limit=args.get("limit"),
            outstanding=args.get("outstanding"), due_date=args.get("dueDate"),
            notes=args.get("notes")
        )
    elif name == "manage_investment":
        return exec_manage_investment(
            action=args.get("action"), ticker=args.get("ticker"),
            platform=args.get("platform"), type_=args.get("type"),
            qty=args.get("qty"), avg_buy=args.get("avgBuy"),
            currency=args.get("currency"), cost_basis=args.get("costBasis"),
            current_price=args.get("currentPrice"), platform_cash=args.get("platformCash"),
            notes=args.get("notes")
        )
    elif name == "manage_loan":
        return exec_manage_loan(
            action=args.get("action"), loan_type=args.get("loanType"),
            lender=args.get("lender"), remaining=args.get("remaining"),
            monthly=args.get("monthly"), rate=args.get("rate"),
            tenor=args.get("tenor"), notes=args.get("notes")
        )
    elif name == "manage_budget":
        return exec_manage_budget(
            action=args.get("action"), category=args.get("category"),
            amount=args.get("amount")
        )
    elif name == "manage_transaction":
        return exec_manage_transaction(
            action=args.get("action"), trx_id=args.get("id"),
            date_str=args.get("date"), type_=args.get("type"),
            category=args.get("category"), account=args.get("account"),
            amount=args.get("amount"), desc=args.get("desc")
        )
    else:
        return json.dumps({"error": f"Unknown tool: {name}"})

# ============================================================
# OLLAMA AGENTIC LOOP
# ============================================================
def chat_with_ollama(messages: list) -> str:
    current = messages.copy()
    for _ in range(6):  # max 6 iterations
        payload = {
            "model": MODEL,
            "messages": current,
            "tools": TOOLS,
            "stream": False,
            "options": {"think": False, "num_ctx": 4096, "num_predict": 1024}
        }
        resp = requests.post(OLLAMA_URL, json=payload, timeout=120)
        resp.raise_for_status()
        data    = resp.json()
        message = data.get("message", {})
        content = message.get("content", "")
        tool_calls = message.get("tool_calls", [])

        if not tool_calls:
            return content or "Maaf, ga ada respons."

        current.append({"role": "assistant", "content": content or "", "tool_calls": tool_calls})

        for tc in tool_calls:
            fn   = tc.get("function", {})
            name = fn.get("name", "")
            args = fn.get("arguments", {})
            if isinstance(args, str):
                try: args = json.loads(args)
                except: args = {}
            result = execute_tool(name, args)
            logger.info(f"✅ Tool result: {result[:120]}...")
            current.append({"role": "tool", "content": result})

    return "Maaf, terlalu banyak iterasi tool call."

# ============================================================
# CONVERSATION HISTORY
# ============================================================
histories: dict = {}

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
# DAILY BRIEF
# ============================================================
async def send_daily_brief(context: ContextTypes.DEFAULT_TYPE):
    """Auto-send morning brief ke semua subscriber."""
    if not subscribers:
        return

    try:
        fx      = json.loads(exec_get_fx_rates())
        markets = json.loads(exec_get_market_data(["^JKSE", "^GSPC"], "5d"))
        crypto  = json.loads(exec_get_crypto_prices(["bitcoin", "ethereum", "solana"]))
        today   = dt.datetime.now().strftime("%d %b %Y")

        # FX block
        rates = fx.get("rates", {})
        def fmt_fx(c): return f"Rp {rates.get(c, 0):,.0f}" if c in rates else "N/A"

        fx_block = (
            f"*💱 FX Rates (vs IDR)*\n"
            f"USD: {fmt_fx('USD')}\n"
            f"EUR: {fmt_fx('EUR')}\n"
            f"CHF: {fmt_fx('CHF')}\n"
            f"JPY: {fmt_fx('JPY')}\n"
            f"CNY: {fmt_fx('CNY')}\n"
            f"SGD: {fmt_fx('SGD')}"
        )

        # Market block
        def fmt_mkt(ticker, name):
            d = markets.get(ticker, {})
            if "error" in d: return f"{name}: N/A"
            chg = d.get("change_pct", 0)
            emoji = "🟢" if chg >= 0 else "🔴"
            return f"{name}: {d.get('price', 0):,.2f} {emoji} {chg:+.2f}%"

        mkt_block = (
            f"*📈 Markets*\n"
            f"{fmt_mkt('^JKSE', 'IHSG')}\n"
            f"{fmt_mkt('^GSPC', 'S&P 500')}"
        )

        # Crypto block
        def fmt_crypto(cid, name):
            d = crypto.get(cid, {})
            if not d: return f"{name}: N/A"
            chg = d.get("change_24h", 0)
            emoji = "🟢" if chg >= 0 else "🔴"
            idr = d.get("idr", 0)
            usd = d.get("usd", 0)
            return f"{name}: ${usd:,.0f} {emoji} {chg:+.1f}% = Rp {idr/1e6:.2f}jt"

        crypto_block = (
            f"*₿ Crypto*\n"
            f"{fmt_crypto('bitcoin', 'BTC')}\n"
            f"{fmt_crypto('ethereum', 'ETH')}\n"
            f"{fmt_crypto('solana', 'SOL')}"
        )

        msg = f"🌅 *Edith Daily Brief — {today}*\n\n{fx_block}\n\n{mkt_block}\n\n{crypto_block}"

        for uid, chat_id in subscribers.items():
            try:
                await context.bot.send_message(chat_id=chat_id, text=msg, parse_mode="Markdown")
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
    # Ollama
    try:
        r = requests.get("http://localhost:11434/api/tags", timeout=5)
        models = [m["name"] for m in r.json().get("models", [])]
        has_model = any("qwen3" in m.lower() for m in models)
        lines.append(f"{'✅' if has_model else '⚠️'} Ollama — {MODEL} {'ready' if has_model else 'NOT FOUND'}")
    except Exception as e:
        lines.append(f"❌ Ollama — {e}")
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
        f"✅ Lo udah subscribe daily brief!\n"
        f"Tiap pagi jam 7 WIB lo dapat update FX, IHSG, SPX & Crypto."
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
    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + get_history(uid)

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
            response = await asyncio.get_event_loop().run_in_executor(
                None, chat_with_ollama, messages
            )
        finally:
            typing_task.cancel()

        add_msg(uid, "assistant", response)

        # Edit placeholder with real response
        try:
            await placeholder.edit_text(response, parse_mode="Markdown")
        except Exception:
            await placeholder.edit_text(response)

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
    logger.info(f"   Model  : {MODEL}")
    logger.info(f"   Finance: {FINANCE_URL}")
    logger.info(f"   Ollama : {OLLAMA_URL}")

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
        time=dt.time(hour=7, minute=0, tzinfo=wib),
        name="daily_brief"
    )
    logger.info("⏰ Daily brief scheduled at 07:00 WIB")

    logger.info("✅ Bot running. Ctrl+C to stop.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
