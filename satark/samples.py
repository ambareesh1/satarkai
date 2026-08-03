"""Curated demo messages (real-world Indian scam styles + a few safe ones).

Used to power the dashboard's one-click "try a sample" buttons.
"""

SAMPLES = [
    {
        "channel": "call",
        "sender": "+919812345678",
        "label": "Digital arrest call",
        "text": (
            "Namaste, main CBI officer bol raha hoon. Aapke Aadhaar par ek parcel "
            "aaya hai jisme illegal narcotics mile hain. Aapke naam par money "
            "laundering ka case darj hua hai. Yeh digital arrest hai, aap Skype par "
            "video call par bane rahein aur kisi ko mat bataiye. Case band karne ke "
            "liye verification amount Rs 45,000 turant is UPI par bhejiye: cbi.verify@ybl"
        ),
    },
    {
        "channel": "sms",
        "sender": "+918877665544",
        "label": "Fake KYC SMS",
        "text": (
            "Dear customer, your SBI account will be BLOCKED today due to incomplete "
            "KYC. Update immediately to avoid suspension: http://sbi-kyc-verify.xyz/login"
        ),
    },
    {
        "channel": "whatsapp",
        "sender": "+917001234567",
        "label": "KBC lottery (WhatsApp)",
        "text": (
            "Congratulations! Aapka WhatsApp number KBC lucky draw me 25,00,000 "
            "jeeta hai. Prize claim karne ke liye registration fee Rs 5,600 is number "
            "par pay karo aur apna bank details bhejo. Jaldi karo offer aaj hi expire."
        ),
    },
    {
        "channel": "sms",
        "sender": "VM-OTPBNK",
        "label": "OTP theft attempt",
        "text": (
            "This is bank security. We detected a fraud on your card. To block it, "
            "please share the 6 digit OTP we just sent you and your CVV for verification."
        ),
    },
    {
        "channel": "email",
        "sender": "refund@incometax-refund.online",
        "subject": "Your Income Tax refund of Rs 15,340 is pending",
        "label": "Tax refund phishing (email)",
        "text": (
            "Dear taxpayer, our records show a refund of Rs 15,340 is pending. "
            "Please verify your account and PAN by clicking the secure link within 24 "
            "hours or the refund will expire: https://bit.ly/it-refund-verify"
        ),
    },
    {
        "channel": "notification",
        "sender": "QuickLoan",
        "label": "Instant loan trap",
        "text": (
            "Your loan of Rs 2,00,000 is PRE-APPROVED! No documents needed. Pay a "
            "small refundable processing fee of Rs 1,999 to disburse instantly. "
            "Limited time, apply now!"
        ),
    },
    {
        "channel": "sms",
        "sender": "AX-AMZN",
        "label": "Safe: real OTP (no ask)",
        "text": "123456 is your Amazon OTP. Do not share it with anyone.",
    },
    {
        "channel": "whatsapp",
        "sender": "+919900112233",
        "label": "Safe: friend message",
        "text": "Hey, are we still meeting at 6pm for coffee near the metro station?",
    },
]
