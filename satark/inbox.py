"""Dummy inbox content for the iPhone simulator.

A realistic mix of scam and legit messages per app, styled like the real thing.
Each item maps to an engine `channel` so tapping it can run a real analysis.

app        -> UI surface (messages / whatsapp / mail / phone / notifications)
channel    -> engine channel (sms / whatsapp / email / call / notification)
"""

from __future__ import annotations

from typing import Any, Dict, List

# app -> engine channel
APP_CHANNEL = {
    "messages": "sms",
    "whatsapp": "whatsapp",
    "mail": "email",
    "phone": "call",
    "notifications": "notification",
}

APP_META = {
    "messages": {"name": "Messages", "icon": "💬", "color": "#34c759"},
    "whatsapp": {"name": "WhatsApp", "icon": "🟢", "color": "#25d366"},
    "mail": {"name": "Mail", "icon": "✉️", "color": "#1a8cff"},
    "phone": {"name": "Phone", "icon": "📞", "color": "#34c759"},
    "notifications": {"name": "Notifications", "icon": "🔔", "color": "#ff9500"},
}


INBOX: List[Dict[str, Any]] = [
    # ---------------- Messages / SMS ---------------- #
    {
        "app": "messages", "sender": "VK-KYCBNK", "name": "SBI Alerts", "avatar": "🏦",
        "time": "09:12", "scam": True,
        "preview": "Your SBI account will be BLOCKED today…",
        "text": "Dear customer, your SBI account will be BLOCKED today due to incomplete KYC. Update immediately to avoid suspension: http://sbi-kyc-verify.xyz/login",
    },
    {
        "app": "messages", "sender": "+918877665544", "name": "Unknown", "avatar": "👤",
        "time": "08:47", "scam": True,
        "preview": "This is bank security. Share the OTP…",
        "text": "This is bank security. We detected a fraud on your card. To block it, please share the 6 digit OTP we just sent you and your CVV for verification.",
    },
    {
        "app": "messages", "sender": "TX-ELECBL", "name": "Electricity", "avatar": "⚡",
        "time": "Yesterday", "scam": True,
        "preview": "Your electricity will be disconnected tonight…",
        "text": "Dear consumer, your electricity will be disconnected tonight 9:30 PM as previous month bill not updated. Contact electricity officer immediately: 9812345678",
    },
    {
        "app": "messages", "sender": "AX-AMZN", "name": "Amazon", "avatar": "📦",
        "time": "Yesterday", "scam": False,
        "preview": "123456 is your Amazon OTP. Do not share…",
        "text": "123456 is your Amazon OTP. Do not share it with anyone.",
    },

    # ---------------- WhatsApp ---------------- #
    {
        "app": "whatsapp", "sender": "+917001234567", "name": "KBC Lucky Draw", "avatar": "🎁",
        "time": "10:30", "scam": True,
        "preview": "Congratulations! Aapka number jeeta hai…",
        "text": "Congratulations! Aapka WhatsApp number KBC lucky draw me 25,00,000 jeeta hai. Prize claim karne ke liye registration fee Rs 5,600 is number par pay karo aur apna bank details bhejo. Jaldi karo offer aaj hi expire.",
    },
    {
        "app": "whatsapp", "sender": "+919812300011", "name": "Rahul Sir (Job)", "avatar": "💼",
        "time": "10:05", "scam": True,
        "preview": "Part time job, earn 5000 daily…",
        "text": "Hello! We offer a part time job, earn Rs 5000 daily just by liking YouTube videos. Simple task based work from home. To start, pay a refundable registration of Rs 1,999 on this UPI: quicktask@ybl. Limited seats, apply now!",
    },
    {
        "app": "whatsapp", "sender": "+919900112233", "name": "Priya", "avatar": "🙂",
        "time": "09:20", "scam": False,
        "preview": "Are we still meeting at 6pm?",
        "text": "Hey, are we still meeting at 6pm for coffee near the metro station?",
    },

    # ---------------- Mail ---------------- #
    {
        "app": "mail", "sender": "refund@incometax-refund.online", "name": "Income Tax Dept",
        "avatar": "🧾", "time": "07:55", "scam": True,
        "subject": "Your Income Tax refund of Rs 15,340 is pending",
        "preview": "Verify your account and PAN within 24 hours…",
        "text": "Dear taxpayer, our records show a refund of Rs 15,340 is pending. Please verify your account and PAN by clicking the secure link within 24 hours or the refund will expire: https://bit.ly/it-refund-verify",
    },
    {
        "app": "mail", "sender": "security@paytm-account-verify.xyz", "name": "Paytm Security",
        "avatar": "🔒", "time": "Yesterday", "scam": True,
        "subject": "Action required: your wallet KYC is on hold",
        "preview": "Re-verify now to avoid permanent suspension…",
        "text": "Your Paytm wallet has been put on hold due to a KYC mismatch. Re-verify your account now to avoid permanent suspension. Click here to update: http://paytm-account-verify.xyz/kyc",
    },
    {
        "app": "mail", "sender": "no-reply@github.com", "name": "GitHub",
        "avatar": "🐙", "time": "Mon", "scam": False,
        "subject": "Your build succeeded",
        "preview": "The workflow run completed successfully.",
        "text": "Hi, your GitHub Actions workflow run for satarkai completed successfully. No action needed.",
    },

    # ---------------- Phone (call transcripts) ---------------- #
    {
        "app": "phone", "sender": "+919812345678", "name": "Unknown (Delhi)", "avatar": "🚔",
        "time": "11:02", "scam": True, "call": True,
        "preview": "Missed call · CBI officer…",
        "text": "Namaste, main CBI officer bol raha hoon. Aapke Aadhaar par ek parcel aaya hai jisme illegal narcotics mile hain. Aapke naam par money laundering ka case darj hua hai. Yeh digital arrest hai, aap Skype par video call par bane rahein aur kisi ko mat bataiye. Case band karne ke liye verification amount Rs 45,000 turant is UPI par bhejiye: cbi.verify@ybl",
    },
    {
        "app": "phone", "sender": "1800-CARE", "name": "Mom", "avatar": "👩",
        "time": "10:10", "scam": False, "call": True,
        "preview": "Incoming call · Mom",
        "text": "Beta, khana kha liya? Shaam ko ghar jaldi aana, aunty aa rahi hain milne.",
    },

    # ---------------- Notifications ---------------- #
    {
        "app": "notifications", "sender": "QuickLoan", "name": "QuickLoan", "avatar": "💰",
        "time": "now", "scam": True,
        "preview": "Your loan of Rs 2,00,000 is PRE-APPROVED!",
        "text": "Your loan of Rs 2,00,000 is PRE-APPROVED! No documents needed. Pay a small refundable processing fee of Rs 1,999 to disburse instantly. Limited time, apply now!",
    },
    {
        "app": "notifications", "sender": "Courier", "name": "FastCourier", "avatar": "📮",
        "time": "5m ago", "scam": True,
        "preview": "Your parcel is held by customs…",
        "text": "Your parcel is held by customs due to illegal items found. Pay customs clearance fee of Rs 3,500 within 2 hours or it will be seized and legal action taken. Pay here: http://parcel-clear.top/pay",
    },
]


def list_inbox() -> List[Dict[str, Any]]:
    items = []
    for i, m in enumerate(INBOX):
        d = dict(m)
        d["id"] = i
        d["channel"] = APP_CHANNEL.get(m["app"], "sms")
        items.append(d)
    return items


def apps_summary() -> List[Dict[str, Any]]:
    """App icons + unread/scam badge counts for the home screen."""
    out = []
    for app, meta in APP_META.items():
        count = sum(1 for m in INBOX if m["app"] == app)
        scam = sum(1 for m in INBOX if m["app"] == app and m.get("scam"))
        out.append({
            "app": app, "name": meta["name"], "icon": meta["icon"],
            "color": meta["color"], "count": count, "badge": scam,
        })
    return out
