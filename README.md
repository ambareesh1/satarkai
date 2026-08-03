# SatarkAI — Multi-Channel Scam Shield

**Satark** (सतर्क) means *alert / vigilant*. SatarkAI is a unified, AI-powered scam-detection
shield that watches every channel a scam can reach you through — **phone calls, SMS,
notifications, WhatsApp messages, and emails** — with a single shared detection brain.

Scams in India are exploding across channels: digital-arrest calls, fake KYC SMS, lottery
WhatsApp forwards, phishing emails. SatarkAI ingests text (or a call transcript), scores the
**scam risk (0–100)**, tells you **which category** and **exactly why**, and gives you clear
**safe-action advice** — in English and Hinglish.

## Highlights

- **One brain, many channels** — a shared Scam Intelligence Engine; each channel is a thin adapter.
- **Analyze-anything box** — paste any SMS / WhatsApp / notification / email → instant verdict.
- **Explainable** — every verdict lists the *reasons* and the *entities* it found
  (UPI IDs, phone numbers, links, amounts, OTP requests).
- **Multilingual signatures** — English + Hindi/Hinglish scam patterns.
- **Runs offline** — the core engine needs only Flask + Python stdlib. No data leaves your machine
  unless you opt into the optional LLM layer.
- **Optional upgrades** — live-call voice monitor (Whisper) and LLM reasoning (OpenRouter).

## Scam categories detected

Digital arrest / police-CBI impersonation · KYC / account-block · OTP / PIN / CVV theft ·
Lottery / prize · Fake job / instant loan · Refund / overpayment · Courier / customs parcel ·
Electricity-disconnection · Investment / crypto "double your money" · Sextortion.

## Quick start

```bash
pip install -r requirements.txt
python app.py
# open http://127.0.0.1:5000
```

Then paste a suspicious message into the **Analyze** box, or click a **sample** to see it flagged.

## Architecture

```
 Voice call ─┐
 SMS ────────┤                                   ┌─ Real-time alert
 Notification┼─► Channel Connectors ─► Message ──► SCAM ENGINE ─► Risk ─┼─ Explanation ("why")
 WhatsApp ───┤     (normalize)         (common)    (rules+LLM)   0–100  ├─ Safe-action advice
 Email ──────┘                                                          └─ Dashboard + history
```

- `satark/engine.py` — orchestrates the pipeline → `Detection`
- `satark/entities.py` — extracts phone/UPI/URL/amount/OTP
- `satark/patterns.py` — multilingual scam signatures
- `satark/reputation.py` — URL & sender heuristics
- `satark/risk.py` — score fusion + advice
- `satark/llm.py` — optional OpenRouter intent + explanation
- `satark/store.py` — SQLite history + feedback
- `app.py` — Flask dashboard

## Channel status

| Channel | v1 (this repo) | Production path |
|---|---|---|
| Paste / forward any message | ✅ live | — |
| Email | ✅ IMAP scan (Gmail app password) | same |
| Voice call | ✅ recording/mic → Whisper | Android CallScreeningService |
| SMS / Notification / WhatsApp | ✅ via paste / Twilio webhook | Android companion app / Twilio |

> Note: personal WhatsApp chats cannot be auto-read (platform policy). SatarkAI uses the
> compliant **forward-a-message-to-the-bot** model, or reads WhatsApp **notifications** via the
> optional Android companion.

## Privacy

All core analysis runs **locally**. The optional LLM layer only activates if you set
`OPENROUTER_API_KEY`, and only then is message text sent to the model for deeper reasoning.
