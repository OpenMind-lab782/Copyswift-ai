import os
import requests
import logging

logger = logging.getLogger("copyswift.email")

RESEND_API_KEY = os.environ.get("RESEND_API_KEY", "").strip()
EMAIL_FROM = os.environ.get(
    "EMAIL_FROM",
    "support@copyswiftai.com"
)

RESEND_URL = "https://api.resend.com/emails"


def send_email(to_email, subject, html):
    """
    Send an email using Resend.
    Returns True on success, False on failure.
    """

    if not RESEND_API_KEY:
        logger.error("RESEND_API_KEY missing.")
        return False

    payload = {
        "from": EMAIL_FROM,
        "to": [to_email],
        "subject": subject,
        "html": html
    }

    headers = {
        "Authorization": f"Bearer {RESEND_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        r = requests.post(
            RESEND_URL,
            json=payload,
            headers=headers,
            timeout=30
        )

        if r.status_code in (200, 201):
            logger.info("Email sent to %s", to_email)
            return True

        logger.error(
            "Resend error %s: %s",
            r.status_code,
            r.text
        )

    except Exception:
        logger.exception("Email sending failed.")

    return False


def welcome_email(name="Customer"):

    return f"""
    <html>
    <body style="font-family:Arial;background:#f4f4f4;padding:30px;">
    <div style="background:white;padding:30px;border-radius:12px;max-width:650px;margin:auto;">

    <h2 style="color:#0b6bff;">
    Welcome to CopySwift AI™ 🚀
    </h2>

    <p>Hello <b>{name}</b>,</p>

    <p>
    Thank you for joining CopySwift AI™.
    </p>

    <p>
    You now have access to powerful AI tools including:
    </p>

    <ul>
        <li>AI Ad Copy</li>
        <li>Campaign Generator</li>
        <li>AI Images</li>
        <li>Image Enhancement</li>
        <li>Talking Videos</li>
    </ul>

    <p>
    Thank you for choosing us.
    </p>

    <hr>

    <small>
    © CopySwift AI™
    </small>

    </div>
    </body>
    </html>
    """


def payment_email(package, credits):

    return f"""
    <html>
    <body style="font-family:Arial;background:#f5f5f5;padding:30px;">

    <div style="background:white;padding:30px;border-radius:12px;max-width:650px;margin:auto;">

    <h2 style="color:green;">
    Payment Successful ✅
    </h2>

    <p>Your payment has been confirmed.</p>

    <p>
    Package:
    <b>{package}</b>
    </p>

    <p>
    Credits Added:
    <b>{credits}</b>
    </p>

    <p>
    Thank you for supporting CopySwift AI™.
    </p>

    </div>
    </body>
    </html>
    """


def crypto_pending_email(tx_hash):

    return f"""
    <html>
    <body style="font-family:Arial;background:#f4f4f4;padding:30px;">

    <div style="background:white;padding:30px;border-radius:12px;max-width:650px;margin:auto;">

    <h2>
    Crypto Payment Received ⏳
    </h2>

    <p>
    Your transaction has been received.
    </p>

    <p>
    Transaction:
    </p>

    <pre>{tx_hash}</pre>

    <p>
    Your credits will be activated after verification.
    </p>

    </div>

    </body>
    </html>
    """
