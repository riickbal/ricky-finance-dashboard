# Ricky Finance Dashboard — AI Integration Roadmap

## Context & Current State

Personal finance dashboard hosted at: **riickbal.github.io/ricky-finance-dashboard**

Tech stack saat ini:
- Pure HTML + CSS + Vanilla JS
- Data di `data.js` (static JS object, `window.DASHBOARD_DATA`)
- Hosted di GitHub Pages
- Input transaksi manual via Claude (Cowork)

Mac Mini M4 (local):
- Ollama sudah running
- Qwen3 sudah loaded
- Open WebUI sudah aktif
- IP lokal sudah diketahui (accessible via WiFi yang sama)

---

## Phase 1 — Backend API ✅ (IN PROGRESS)

**Goal:** Dashboard baca/tulis data dari SQLite via Express API, bukan dari static data.js lagi.

Stack: Node.js + Express + SQLite (better-sqlite3)

### File structure
```
backend/
├── package.json
├── server.js       ← Express API, port 3000
├── schema.sql      ← table definitions
├── migrate.js      ← one-time import dari data.js → SQLite
└── finance.db      ← SQLite database (auto-generated)
```

### API Endpoints
| Method | Endpoint | Function |
|--------|----------|----------|
| GET | /api/data | Full dashboard payload (same shape as data.js) |
| POST | /api/transactions | Tambah transaksi baru |
| PATCH | /api/banks/:nick | Update saldo bank |
| PATCH | /api/creditcards/:name | Update CC outstanding |
| PATCH | /api/investments/:ticker | Update harga investasi |
| PATCH | /api/fxrate | Update kurs USD/IDR |

### Transaction JSON Schema (untuk AI agent)
```json
{
  "id": "t71",
  "date": "YYYY-MM-DD",
  "type": "Out | In | Transfer | Accrual",
  "category": "Meals | Transportation | Kebutuhan Dasar Anak | ...",
  "account": "BCA 062 | BCA 968 | BLU 904 | Permata 829 | ...",
  "amount": 50000,
  "desc": "deskripsi bebas"
}
```

### Dashboard update
- index.html: ganti `<script src="data.js">` → `fetch(API_URL + '/api/data')`
- `API_URL` = config variable di top of script (isi IP Mac Mini)
- Fallback ke data.js kalau API unreachable

### Run di Mac Mini
```bash
cd backend
npm install
node migrate.js   # sekali aja, import existing data
node server.js    # start API
```

---

## Phase 2 — Cloudflare Tunnel

**Goal:** Dashboard & API accessible dari internet (bukan cuma WiFi lokal).

Kenapa perlu: biar bisa akses dashboard dari HP di luar rumah, dan Telegram bot bisa hit API dari mana aja.

### Steps
1. Buat Cloudflare account (gratis)
2. Install `cloudflared` di Mac Mini:
   ```bash
   brew install cloudflare/cloudflare/cloudflared
   ```
3. Login & buat tunnel:
   ```bash
   cloudflared tunnel login
   cloudflared tunnel create ricky-finance
   ```
4. Config tunnel expose `localhost:3000`
5. Dapat public URL: `https://ricky-finance.cfargotunnel.com` (atau custom domain)
6. Update `API_URL` di index.html ke tunnel URL
7. Setup tunnel sebagai launchd service (auto-start saat Mac Mini nyala)

**Hasil:** Dashboard + API live di internet, no port forwarding, no static IP needed.

---

## Phase 3 — Qwen3 Prompt Engineering

**Goal:** Qwen3 bisa parse pesan natural language → structured JSON → POST ke API.

### System Prompt untuk Qwen3 (Finance Agent)
Qwen3 harus di-brief dengan:
1. Daftar kategori expense yang valid
2. Daftar account names yang valid
3. Format JSON output yang exact
4. Contoh few-shot (input → output)
5. Rules: kalau ga yakin → tanya, jangan asumsiin

### Contoh few-shot
```
Input: "makan siang warteg 25rb BCA 062"
Output:
{
  "date": "{{today}}",
  "type": "Out",
  "category": "Meals",
  "account": "BCA 062",
  "amount": 25000,
  "desc": "Makan siang warteg"
}

Input: "bensin 50rb dari 968"
Output:
{
  "date": "{{today}}",
  "type": "Out",
  "category": "Transportation",
  "account": "BCA 968",
  "amount": 50000,
  "desc": "Bensin"
}

Input: "gaji masuk 20jt permata"
Output:
{
  "date": "{{today}}",
  "type": "In",
  "category": "Income - Salary",
  "account": "Permata 829",
  "amount": 20000000,
  "desc": "Gaji bulanan"
}
```

### Confidence routing
- Qwen3 output confidence score (0-1)
- Score ≥ 0.85 → langsung POST ke API
- Score < 0.85 → forward ke Claude API untuk validasi/enrichment
- Claude confirm → POST ke API

---

## Phase 4 — AI Mandor + Telegram/WA

**Goal:** Lo bisa input transaksi & query dashboard via chat (Telegram/WA).

### Architecture
```
Telegram / WA
    ↓
AI Mandor (orchestrator)
    ↓ routing berdasarkan intent
    ├── Finance Agent (Qwen3) → POST /api/transactions
    ├── Query Agent            → GET /api/data → format laporan
    └── [Future agents...]
```

### AI Mandor responsibilities
1. **Intent detection** — ini transaksi baru? query data? update saldo?
2. **Routing** — kirim ke agent yang tepat
3. **Response formatting** — format jawaban balik ke user (bukan raw JSON)
4. **Error handling** — kalau agent gagal, fallback atau tanya ulang

### Setup options
- **n8n** (recommended) — visual workflow, self-hosted di Mac Mini, bisa connect Telegram bot + HTTP requests
- **FastAPI** — lebih custom, lebih flexible, lebih coding
- **Webhook sederhana** — minimal setup, less features

### Telegram Bot flow
```
User: "kemarin beli kopi 35rb BCA"
  → Mandor: deteksi = transaksi baru
  → Finance Agent (Qwen3): parse → JSON
  → POST /api/transactions
  → Response: "✅ Dicatat: Meals Rp35,000 dari BCA 062 (2026-06-26)"
```

### WA flow (via Twilio / WA Business API)
Sama seperti Telegram, tapi butuh WA Business account atau Twilio sandbox.

---

## Valid Categories (reference untuk prompt engineering)

### OPEX
- Meals
- Groceries
- Listrik
- Kebutuhan Dasar Anak
- Mainan & Edukasi Anak
- Wifi & Internet
- Transportation
- Service Vehicle
- Phone Credit
- Wellness (Hobbies & Travel)
- Apps & Subscriptions
- Electronics & Accessories
- Marketplace / Other

### Other Expenses
- Interest Expense - KTA
- Interest Expense - KPR
- Biaya Admin/Fee
- Lain-lain / Belum Jelas

### Non-expense (Balance Sheet)
- Transfer Internal
- Liability Payment - CC
- Liability Payment - KTA
- Liability Payment - KPR
- Fixed Asset Purchase
- Receivable

### Income
- Income - Salary
- Income - Other

## Valid Accounts (reference)
- BLU 904
- BCA 062
- BCA 968
- Permata 829
- Permata 734
- CIMB 200
- CC CIMB
- CC Permata

---

## Progress Tracker

| Phase | Status |
|-------|--------|
| Phase 1 — Backend API | 🔄 In Progress |
| Phase 2 — Cloudflare Tunnel | ⏳ Pending (butuh CF account) |
| Phase 3 — Qwen3 Prompt Engineering | ⏳ Pending |
| Phase 4 — AI Mandor + Telegram | ⏳ Pending |
