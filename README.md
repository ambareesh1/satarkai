# SatarkAI — Multi-Channel Scam Shield

**Satark** (सतर्क) means *alert / vigilant*.

SatarkAI is a local, explainable scam-detection shield for **phone calls, SMS, WhatsApp, notifications, and email**. Paste a message (or a call transcript). One rule engine scores **scam risk 0–100**, names the **category**, lists **why**, extracts **UPI / links / OTP asks**, and tells you the **safe next step** — in English and Hinglish.

The **rule engine is the production path**. Optional LLM, ElevenLabs voice, and SMTP email only add on top. The app runs fully without any API keys.

---

## What you get

| Surface | What it does |
|---|---|
| **Home** `http://127.0.0.1:7000/` | Bright landing page that explains SatarkAI, channels, and scam types |
| **Dashboard** `http://127.0.0.1:7000/dashboard` | Phone simulator + Analyze box + history + daily report |
| **Rule engine** | Always on. Scores every message locally |
| **Voice alerts** | Optional. Toggle **Web voice** on/off in the header |
| **Daily report** | Counts scams / suspicious / safe for today; email if SMTP is set |

**Categories the engine looks for:** digital arrest / police–CBI impersonation · KYC / account-block · OTP / PIN / CVV theft · lottery / prize · fake job / instant loan · refund / overpayment · courier / customs parcel · electricity-disconnection · investment / crypto “double your money” · sextortion.

---

## 1. Prerequisites

1. Install **Python 3.10+** (3.12 is tested). On Windows, tick **Add python.exe to PATH**.
2. Confirm it works:

```bash
python --version
```

3. (Optional) Git, if you are cloning from GitHub.

---

## 2. Get the code

```bash
git clone https://github.com/ambareesh1/satarkai.git
cd satarkai
```

If you already have the folder, skip clone and `cd` into the project root (`SatarkAI` / `satarkai`).

---

## 3. Create a virtual environment (recommended)

**Windows (PowerShell):**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks scripts: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`, then activate again.

**macOS / Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

You should see `(.venv)` in the prompt.

---

## 4. Install dependencies

From the project root:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

This installs:

- **Flask** — web app
- **waitress** — production WSGI server (used automatically on `python app.py`)
- **requests** — used only if you enable optional LLM / ElevenLabs

No API keys are required for this step.

---

## 5. Run the app

```bash
python app.py
```

You should see:

```text
SatarkAI ready  http://127.0.0.1:7000  (rule engine live)
```

Then open:

| Page | URL |
|---|---|
| Home | http://127.0.0.1:7000/ |
| Dashboard | http://127.0.0.1:7000/dashboard |
| Health | http://127.0.0.1:7000/health |

Stop the server with `Ctrl+C` in that terminal.

**If port 7000 is already in use**, either close the old process or set a new port:

```powershell
$env:SATARK_PORT="7001"
python app.py
```

```bash
SATARK_PORT=7001 python app.py
```

---

## 6. Use the product (step by step)

### 6.1 Home page

1. Open http://127.0.0.1:7000/
2. Read what SatarkAI is, which channels it covers, and which scam scripts it catches.
3. Click **Open the shield** / **Try it on a real message** to go to the dashboard.

### 6.2 Dashboard — phone simulator

1. Open http://127.0.0.1:7000/dashboard
2. On the **black iPhone**, tap **Messages**, **WhatsApp**, **Mail**, **Phone**, or **Notifications**.
3. Tap a conversation. The Analyze form fills automatically.
4. Tap **Scan with SatarkAI**.
5. Read the in-phone alert (SCAM / SUSPICIOUS / SAFE, score, advice).
6. The same verdict appears in the Analyze card, Overview stats, and Recent activity.

Safe samples (Amazon OTP, a friend chat, Mom’s call, GitHub mail) should stay **SAFE**. Scam samples should score **SCAM**.

### 6.3 Dashboard — paste your own message

1. Pick a **channel** (Phone Call, SMS, WhatsApp, Notification, Email).
2. Optionally fill **Sender** (and **Subject** for email).
3. Paste the full text into **Message**.
4. Click **Analyze** (or `Ctrl+Enter` / `Cmd+Enter`).
5. Check:
   - risk gauge **0–100**
   - level + category
   - **Why flagged**
   - **Detected entities** (UPI, links, phones, amounts, OTP terms)
   - **Was this right?** feedback buttons

### 6.4 Turn voice off / on

The header **🔊 Web voice** button is a real toggle (not just a label).

1. Click **🔊 Web voice** → it becomes **🔇 Voice off**. Speech stops; the choice is remembered.
2. Click again to turn alerts back on.
3. If ElevenLabs is configured, the label reads **🔊 ElevenLabs** instead.

### 6.5 Daily report

1. Click **Daily Report**.
2. Review today’s scams, suspicious, and safe counts.
3. **Email me this report** works only after SMTP is set in `.env` (see step 8).

---

## 7. How the rule engine works

Every channel is normalized into one `Message`. Then:

1. **Entities** — UPI IDs, URLs, phones, amounts, OTP/PIN/CVV words (`satark/entities.py`)
2. **Patterns** — English + Hindi/Hinglish signatures per scam category (`satark/patterns.py`)
3. **Reputation** — throwaway TLDs, shorteners, fake bank/Paytm-style domains (`satark/reputation.py`)
4. **Fusion** — points → 0–100, then **SAFE ≤ 39**, **SUSPICIOUS 40–69**, **SCAM ≥ 70** (`satark/risk.py`)

Optional **OpenRouter LLM** can refine wording. It **cannot** talk a rule-engine SCAM down to SAFE.

History is stored in local SQLite (`satark.db` in the project folder). Database files are gitignored.

---

## 8. Optional configuration (`.env`)

The app runs with **zero keys**. Only add what you want.

1. Copy the example file:

```bash
copy .env.example .env
```

```bash
cp .env.example .env
```

2. Uncomment and fill lines in `.env`. Existing OS environment variables win over the file.

| Variable | Purpose | Required? |
|---|---|---|
| `OPENROUTER_API_KEY` | Smarter explanations via OpenRouter | No |
| `OPENROUTER_MODEL` | Model id (default `openai/gpt-4o-mini`) | No |
| `SATARK_USE_LLM` | Set `0` to force rules only | No |
| `ELEVENLABS_API_KEY` | Realistic TTS instead of browser voice | No |
| `ELEVENLABS_VOICE_ID` | Voice id (default Rachel) | No |
| `SMTP_HOST` / `SMTP_PORT` / `SMTP_USER` / `SMTP_PASSWORD` | Email the daily report | No |
| `REPORT_TO` | Report recipient (defaults to `SMTP_USER`) | No |
| `SATARK_PORT` | Listen port (default `7000`) | No |
| `SATARK_HOST` | Bind address (default `0.0.0.0`) | No |
| `SATARK_SECRET` | Flask secret (default is for local use) | No |
| `SATARK_DB` | Alternate SQLite path | No |
| `WHISPER_MODEL` | Size for optional `faster-whisper` ASR | No |

Restart `python app.py` after changing `.env`.

**Gmail SMTP:** create a Google **App Password**, then:

```
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=you@gmail.com
SMTP_PASSWORD=your_app_password
REPORT_TO=you@gmail.com
```

---

## 9. Verify it works (tests)

From the project root, with the venv active:

```bash
python tools/engine_test.py
python tools/smoke_test.py
python tools/app_test.py
```

| Script | What it checks |
|---|---|
| `tools/engine_test.py` | Every sample + inbox fixture: scams → SCAM, safe → SAFE |
| `tools/smoke_test.py` | Prints scores for bundled samples |
| `tools/app_test.py` | Flask routes (`/`, `/dashboard`, `/health`, `/analyze`, …) |

Health JSON when the engine is live:

```json
{"ok": true, "engine": "rules", "engine_ready": true, "llm": false, "voice": false, "email": false}
```

---

## 10. Project layout

```
satarkai/
├── app.py                 Flask app + JSON API (Waitress in production)
├── requirements.txt
├── .env.example           Optional keys (copy to .env)
├── templates/
│   ├── home.html          Landing page
│   └── index.html         Dashboard
├── static/
│   ├── css/home.css
│   ├── js/home.js
│   ├── js/app.js          Dashboard (analyze, phone, voice toggle)
│   └── images/            Home-page photos
├── satark/
│   ├── engine.py          Orchestrates rules (+ optional LLM)
│   ├── risk.py            Score fusion
│   ├── patterns.py        Scam signatures
│   ├── entities.py        UPI / URL / OTP extraction
│   ├── reputation.py      Domain / sender heuristics
│   ├── store.py           SQLite history
│   ├── inbox.py           iPhone demo messages
│   ├── samples.py         Extra demo texts
│   ├── llm.py             Optional OpenRouter
│   ├── tts.py             Optional ElevenLabs
│   ├── mailer.py          Optional SMTP
│   ├── report.py          Daily report
│   ├── asr.py             Optional faster-whisper (if installed)
│   └── env.py             .env loader
└── tools/                 engine_test, smoke_test, app_test
```

---

## 11. HTTP API

Base URL: `http://127.0.0.1:7000`

| Method | Path | Notes |
|---|---|---|
| GET | `/` | Home page |
| GET | `/dashboard` | Analyzer UI |
| GET | `/health` | Engine / LLM / voice / email flags |
| POST | `/analyze` | JSON `{ "text", "channel", "sender?", "subject?" }` → verdict |
| GET | `/apps` | Phone home-screen apps + badges |
| GET | `/inbox` | Simulator messages |
| GET | `/samples` | Curated samples |
| GET | `/history` | Recent detections |
| GET | `/stats` | Counts by level / channel |
| POST | `/feedback` | `{ "id", "label": "scam" \| "safe" }` |
| GET | `/report/daily` | Today’s report JSON |
| POST | `/report/email` | Email the report (needs SMTP) |
| POST | `/tts` | MP3 if ElevenLabs is set; otherwise `204` |

Analyze example:

```bash
curl -X POST http://127.0.0.1:7000/analyze ^
  -H "Content-Type: application/json" ^
  -d "{\"text\":\"Your SBI account will be BLOCKED today. Update KYC: http://sbi-kyc-verify.xyz/login\",\"channel\":\"sms\"}"
```

`channel` must be one of: `call`, `sms`, `whatsapp`, `notification`, `email`.

---

## 12. Privacy and reporting real scams

- Core scoring runs **on your machine**. Nothing is sent out unless you set `OPENROUTER_API_KEY` (LLM) or ElevenLabs / SMTP.
- Do not commit `.env` or `*.db` files (they are gitignored).
- Personal WhatsApp chats cannot be auto-read (platform policy). Paste or forward the text into SatarkAI.
- If a message is a real scam, report it at **https://cybercrime.gov.in** or call **1930**.

---

## 13. Troubleshooting

| Problem | What to try |
|---|---|
| `python` not found | Reinstall Python and enable PATH, or use `py -3` |
| Port already in use | Stop the old `python app.py`, or set `SATARK_PORT` |
| Dashboard looks old | Hard-refresh the browser (`Ctrl+F5`) |
| Voice will not stop | Click **🔊 Web voice** until it shows **🔇 Voice off** |
| Rule engine looks “off” | Header should say **Rule engine · live**. Run `python tools/engine_test.py` |
| Analyze error | Keep text under 8000 characters; check the terminal traceback |
| Email report disabled | Set `SMTP_*` in `.env` and restart |
| Tests write `test_satark.db` | Safe to delete; gitignored |
