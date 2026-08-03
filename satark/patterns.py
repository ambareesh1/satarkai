"""Multilingual scam signature library.

Each category has weighted keyword/phrase groups (English + Hindi/Hinglish
transliteration) and a piece of safe-action advice. The engine sums the weight
of matched groups per category and picks the strongest.

`weight` guidance:
    3 = near-certain scam tell (e.g. "digital arrest", "share your OTP")
    2 = strong indicator
    1 = weak / contextual indicator
"""

from __future__ import annotations

from typing import Dict, List

# Words that signal manufactured urgency / pressure - a cross-cutting scam tell.
URGENCY_TERMS: List[str] = [
    "urgent", "immediately", "right now", "within 24 hours", "within 2 hours",
    "last warning", "final notice", "act now", "expire", "expiry", "today only",
    "turant", "abhi", "jaldi", "aaj hi", "warna", "nahi to", "band ho jayega",
]

# Threat / fear terms.
THREAT_TERMS: List[str] = [
    "arrest", "warrant", "police", "cbi", "court", "legal action", "case",
    "jail", "fir", "non-bailable", "seized", "suspend", "block", "deactivate",
    "giraftar", "giraftari", "kanooni", "mukadma",
]


CATEGORIES: Dict[str, Dict] = {
    "digital_arrest": {
        "label": "Digital Arrest / Police impersonation",
        "advice": "No real police, CBI, or court ever arrests you over a call/video or asks for money. Hang up and call 1930 (cyber helpline).",
        "groups": [
            (3, ["digital arrest", "digital house arrest"]),
            (3, ["money laundering", "your aadhaar is linked", "aadhaar misused", "your number will be blocked by trai", "parcel contains drugs", "illegal parcel", "narcotics"]),
            (2, ["cbi", "central bureau", "cyber crime branch", "customs department", "enforcement directorate", "ncb", "fedex parcel", "your parcel is seized"]),
            (2, ["arrest warrant", "non-bailable warrant", "court notice", "legal case against you", "verify on skype", "stay on video call"]),
            (2, ["mumbai police", "delhi police", "cbi officer", "police station", "aapke naam par", "case darj"]),
            (1, ["do not tell anyone", "kisi ko mat batao", "confidential investigation"]),
        ],
    },
    "kyc_account": {
        "label": "KYC / Account-block",
        "advice": "Banks never ask you to update KYC via a link or call. Open your bank app directly or visit a branch. Don't click the link.",
        "groups": [
            (3, ["kyc update", "kyc pending", "kyc expire", "update your kyc", "kyc suspend", "complete your kyc"]),
            (3, ["account will be blocked", "account blocked", "account suspended", "khata band", "account deactivate"]),
            (2, ["pan card update", "link your pan", "update pan", "aadhaar update", "verify your account", "re-verify"]),
            (2, ["net banking blocked", "debit card blocked", "card will be deactivated", "reward points expire", "redeem your points"]),
            (1, ["click the link to update", "click here to verify", "neeche diye link", "link par click"]),
        ],
    },
    "otp_pin": {
        "label": "OTP / PIN / CVV theft",
        "advice": "NEVER share an OTP, PIN, CVV, or password with anyone - not even 'bank staff'. Legit staff never ask for it.",
        "groups": [
            (3, ["share the otp", "share your otp", "tell me the otp", "otp bataye", "otp share", "send the otp", "otp batao", "read the otp", "share the code", "share the 6 digit", "digit otp", "otp we just sent", "otp we sent"]),
            (3, ["share your cvv", "tell me your cvv", "share your pin", "enter your pin", "your card number and cvv", "your cvv for", "and your cvv", "cvv for verification"]),
            (2, ["6 digit code", "verification code i sent", "code you received", "otp aaya hoga", "the 6 digit", "your otp", "your pin", "your cvv"]),
            (1, ["for verification purpose", "to confirm it is you", "block it"]),
        ],
    },
    "lottery_prize": {
        "label": "Lottery / Prize",
        "advice": "You cannot win a lottery you never entered. Any 'prize' that needs a fee or your details first is a scam.",
        "groups": [
            (3, ["you have won", "you won", "lucky winner", "lottery winner", "aap jeet gaye", "aapko mila hai", "jeeta hai", "aapne jeeta", "number jeeta"]),
            (3, ["kbc lottery", "kaun banega crorepati", "kbc lucky", "jio lottery", "whatsapp lottery", "lucky draw winner", "lucky draw me", "lucky draw"]),
            (2, ["prize money", "cash prize", "gift worth", "claim your prize", "prize claim", "claim karne", "inaam", "lottery"]),
            (2, ["pay processing fee", "pay registration fee", "registration fee", "small fee to claim", "gst charge to release", "refundable deposit", "bank details bhejo", "send your bank details"]),
            (1, ["congratulations", "mubarak ho", "you are selected"]),
        ],
    },
    "job_loan": {
        "label": "Fake job / Instant loan",
        "advice": "Real jobs don't charge a registration fee, and real lenders don't approve loans before you apply. Never pay to get paid.",
        "groups": [
            (3, ["pay registration fee for job", "job registration fee", "security deposit for job", "pay to get the job"]),
            (3, ["loan approved", "loan is approved", "pre-approved loan", "loan pre-approved", "is pre-approved", "pre approved", "instant loan", "loan without documents", "no documents needed", "loan disbursed", "disburse instantly", "processing fee for loan", "refundable processing fee"]),
            (2, ["work from home earn", "part time job earn", "earn daily", "earn per day", "ghar baithe kamaye", "roz kamaye", "task based job", "like and subscribe task", "rate the hotel task", "loan of rs", "loan of ₹", "processing fee of"]),
            (2, ["telegram task", "prepaid task", "recharge task", "commission after task"]),
            (1, ["no experience needed", "limited seats", "hurry apply now", "apply now"]),
        ],
    },
    "refund_overpayment": {
        "label": "Refund / Overpayment trick",
        "advice": "A 'refund' that needs you to install an app, share an OTP, or scan a QR to RECEIVE money is a trap - scanning/QR sends money OUT.",
        "groups": [
            (3, ["scan this qr to receive", "scan qr for refund", "scan to get refund", "accept the refund request", "approve the collect request"]),
            (3, ["you paid extra", "double payment", "overpaid", "we will refund", "refund of rs", "electricity refund", "tax refund"]),
            (2, ["install anydesk", "install teamviewer", "install quick support", "screen share app", "remote access"]),
            (1, ["refund", "cashback", "money back"]),
        ],
    },
    "courier_parcel": {
        "label": "Courier / Customs parcel",
        "advice": "Couriers don't call demanding fees or claim your parcel has drugs. Ignore and verify on the courier's official website.",
        "groups": [
            (3, ["your parcel is held", "parcel seized by customs", "illegal items in your parcel", "parcel contains", "customs clearance fee"]),
            (2, ["fedex", "dhl", "bluedart", "india post", "courier company", "delivery failed pay", "reschedule delivery fee"]),
            (1, ["package on hold", "shipment held", "pending delivery"]),
        ],
    },
    "electricity_bill": {
        "label": "Electricity-disconnection",
        "advice": "Electricity boards send official bills, not personal-number SMS threats. Never click the link or call the number - check your provider app.",
        "groups": [
            (3, ["electricity will be disconnected", "power will be cut tonight", "bijli kat di jayegi", "electricity disconnect tonight"]),
            (2, ["update electricity bill", "previous month bill not updated", "contact electricity officer", "bijli bill"]),
            (1, ["disconnect", "power supply", "meter"]),
        ],
    },
    "investment": {
        "label": "Investment / Crypto fraud",
        "advice": "Guaranteed or 'double your money' returns don't exist. Stock/crypto tips in random WhatsApp/Telegram groups are pump-and-dump scams.",
        "groups": [
            (3, ["double your money", "guaranteed return", "guaranteed profit", "100% profit", "paisa double", "risk free profit"]),
            (2, ["crypto investment", "trading tips", "stock tips", "vip trading group", "investment plan", "daily profit", "high return"]),
            (2, ["join our telegram for tips", "expert trader", "insider tip", "ipo allotment guaranteed"]),
            (1, ["invest now", "limited slots", "profit booked"]),
        ],
    },
    "sextortion": {
        "label": "Sextortion / Blackmail",
        "advice": "Don't pay and don't panic. Stop replying, block them, keep evidence, and report at cybercrime.gov.in or call 1930.",
        "groups": [
            (3, ["i have recorded", "screen recorded", "your video is recorded", "leak your video", "viral your video", "nude video"]),
            (3, ["pay or i will send", "send money or i post", "share to your contacts", "family ko bhej dunga"]),
            (2, ["video call recording", "objectionable video", "compromising video"]),
        ],
    },
}


def scan(text: str) -> Dict[str, Dict]:
    """Match `text` against all categories.

    Returns {category_id: {"score": int, "matched": [phrases...]}} for
    every category that had at least one hit.
    """
    low = (text or "").lower()
    results: Dict[str, Dict] = {}
    for cat_id, cat in CATEGORIES.items():
        score = 0
        matched: List[str] = []
        for weight, phrases in cat["groups"]:
            hit = False
            for phrase in phrases:
                if phrase in low:
                    matched.append(phrase)
                    hit = True
            if hit:
                score += weight
        if score > 0:
            results[cat_id] = {"score": score, "matched": matched}
    return results


def find_terms(text: str, terms: List[str]) -> List[str]:
    low = (text or "").lower()
    return [t for t in terms if t in low]
