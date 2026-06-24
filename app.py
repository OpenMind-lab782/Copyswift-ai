from dotenv import load_dotenv
load_dotenv()
from flask import Flask, render_template_string, render_template, request, session, redirect, jsonify
from groq import Groq
import os, hashlib, json, requests, time, sqlite3, base64
import cloudinary
import cloudinary.uploader
from datetime import datetime, timedelta, timedelta
from functools import wraps
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "copyswift-secret-2024")
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

DB_PATH = "copyswift.db"
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin123")

PAYSTACK_SECRET = os.environ.get("PAYSTACK_SECRET_KEY", "")
CASHAPP_TAG = os.environ.get("CASHAPP_TAG", "$YourCashTag")
CASHAPP_AMOUNT = 5

# --- Pay-Per-Ad Credit Packages -------------------------------------------
CREDIT_PACKAGES = {
    "basic": {"label": "Basic",  "ads": 120, "usd": 18},
    "elite": {"label": "Elite",  "ads": 180, "usd": 25},
    "mini": {"label": "Mini", "ads": 10, "usd": 2},
    "starter": {"label": "Starter", "ads": 50, "usd": 8},
    "pro": {"label": "Pro", "ads": 100, "usd": 15},
}
FALLBACK_USD_NGN_RATE = 1600.0  # used only if live rate fetch fails

# --- Together AI + Cloudinary Config ---------------------------------------
TOGETHER_API_KEY = os.environ.get("TOGETHER_API_KEY", "")
cloudinary.config(
    cloud_name=os.environ.get("CLOUDINARY_CLOUD_NAME", ""),
    api_key=os.environ.get("CLOUDINARY_API_KEY", ""),
    api_secret=os.environ.get("CLOUDINARY_API_SECRET", "")
)

def generate_image_and_upload(prompt):
    """Call Together AI FLUX.1-schnell, upload result to Cloudinary, return URL."""
    try:
        headers = {
            "Authorization": f"Bearer {TOGETHER_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "black-forest-labs/FLUX.1-schnell",
            "prompt": prompt,
            "width": 1024,
            "height": 1024,
            "steps": 4,
            "n": 1,
            "response_format": "url"
        }
        resp = requests.post(
            "https://api.together.xyz/v1/images/generations",
            headers=headers,
            json=payload,
            timeout=60
        )
        resp.raise_for_status()
        data = resp.json()
        image_url = data["data"][0]["url"]
        upload_result = cloudinary.uploader.upload(
            image_url,
            folder="copyswift_ai",
            resource_type="image"
        )
        return upload_result.get("secure_url", "")
    except Exception as e:
        print(f"Image generation error: {e}")
        return ""

def get_usd_ngn_rate():
    """Fetch a live USD->NGN exchange rate. Falls back to a fixed rate on error."""
    try:
        r = requests.get("https://open.er-api.com/v6/latest/USD", timeout=6)
        data = r.json()
        rate = data.get("rates", {}).get("NGN")
        if rate:
            return float(rate)
    except Exception:
        pass
    return FALLBACK_USD_NGN_RATE

def usd_to_kobo(usd_amount):
    rate = get_usd_ngn_rate()
    ngn = usd_amount * rate
    return int(round(ngn * 100)), round(ngn, 2), rate

CRYPTO_WALLETS = {
    "BNB":  {"address": os.environ.get("BNB_WALLET",  "YOUR_BNB_ADDRESS"),  "network": "BEP-20 (BSC)", "rate": 0.0016, "icon": "🟡"},
    "TRX":  {"address": os.environ.get("TRX_WALLET",  "YOUR_TRX_ADDRESS"),  "network": "TRON",         "rate": 3.0,    "icon": "🔴"},
    "USDT": {"address": os.environ.get("USDT_WALLET", "YOUR_USDT_ADDRESS"), "network": "TRC-20",       "rate": 1.0,    "icon": "🟢"},
    "MATIC":{"address": os.environ.get("MATIC_WALLET","YOUR_MATIC_ADDRESS"),"network": "Polygon",      "rate": 1.6,    "icon": "🟣"},
    "TON":  {"address": os.environ.get("TON_WALLET",  "YOUR_TON_ADDRESS"),  "network": "TON",          "rate": 0.4,    "icon": "🔵"},
}

PROMO_CODES = {"GODSHELP": True, "COPYSWIFT": True, "PROLAUNCH": True}

COPY_TYPES = {
    "ad":           {"label": "📣 Facebook / Instagram Ad",  "prompt": "Write a short high-converting Facebook/Instagram ad for {product} targeting {audience}. Include a hook, benefit, and CTA. Use emojis."},
    "whatsapp":     {"label": "💬 WhatsApp Sales Message",   "prompt": "Write a persuasive WhatsApp sales message for {product} targeting {audience}. Conversational, under 100 words. Use emojis."},
    "email":        {"label": "📧 Email Campaign",           "prompt": "Write a high-converting sales email for {product} targeting {audience}. Include subject line, hook, benefits, CTA."},
    "product_desc": {"label": "🛒 Product Description",      "prompt": "Write a compelling product description for {product} targeting {audience}. Highlight benefits, features, end with buy CTA."},
    "social_bio":   {"label": "✨ Social Media Bio",         "prompt": "Write a punchy social media bio for a business selling {product} to {audience}. Max 150 chars. Use emojis."},
    "sms":          {"label": "📱 SMS / Short Promo",        "prompt": "Write a short SMS promo for {product} targeting {audience}. Max 160 chars. Include offer and CTA."},
}

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as db:
        db.execute("""CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL, method TEXT NOT NULL,
            amount TEXT, tx_ref TEXT, coin TEXT,
            status TEXT DEFAULT 'pending',
            created_at TEXT DEFAULT (datetime('now')),
            activated_at TEXT)""")
        db.execute("""CREATE TABLE IF NOT EXISTS pro_users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            activated_at TEXT DEFAULT (datetime('now')),
            activated_by TEXT DEFAULT 'auto')""")
        db.execute("CREATE TABLE IF NOT EXISTS free_usage (id INTEGER PRIMARY KEY AUTOINCREMENT, fingerprint TEXT UNIQUE NOT NULL, count INTEGER DEFAULT 0, week_start TEXT)")
        db.execute("CREATE TABLE IF NOT EXISTS credits (email TEXT PRIMARY KEY, balance INTEGER DEFAULT 0)")
        db.execute("""CREATE TABLE IF NOT EXISTS credit_purchases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL, package TEXT NOT NULL,
            ads INTEGER NOT NULL, amount_usd REAL NOT NULL,
            amount_local TEXT, method TEXT NOT NULL,
            tx_ref TEXT, status TEXT DEFAULT 'pending',
            created_at TEXT DEFAULT (datetime('now')),
            activated_at TEXT)""")
        db.execute("CREATE TABLE IF NOT EXISTS affiliates (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, email TEXT UNIQUE NOT NULL, ref_code TEXT UNIQUE NOT NULL, wallet_coin TEXT DEFAULT 'USDT', wallet_address TEXT DEFAULT '', total_earned REAL DEFAULT 0, pending_payout REAL DEFAULT 0, created_at TEXT DEFAULT (datetime('now')))")
        db.execute("CREATE TABLE IF NOT EXISTS referrals (id INTEGER PRIMARY KEY AUTOINCREMENT, ref_code TEXT NOT NULL, subscriber_email TEXT NOT NULL, amount_earned REAL DEFAULT 2.0, status TEXT DEFAULT 'pending', created_at TEXT DEFAULT (datetime('now')), paid_at TEXT)")
        db.execute("CREATE TABLE IF NOT EXISTS customer_referrals (email TEXT PRIMARY KEY, ref_code TEXT NOT NULL, created_at TEXT DEFAULT (datetime('now')))")
        try:
            db.execute("ALTER TABLE credit_purchases ADD COLUMN ref_code TEXT DEFAULT \'\'")
        except Exception:
            pass
        try:
            db.execute("ALTER TABLE referrals ADD COLUMN tx_ref TEXT DEFAULT \'\'")
        except Exception:
            pass
        db.execute("CREATE TABLE IF NOT EXISTS free_usage (id INTEGER PRIMARY KEY AUTOINCREMENT, fingerprint TEXT UNIQUE NOT NULL, count INTEGER DEFAULT 0, week_start TEXT)")
        db.execute("CREATE TABLE IF NOT EXISTS affiliates (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, email TEXT UNIQUE NOT NULL, ref_code TEXT UNIQUE NOT NULL, wallet_coin TEXT DEFAULT 'USDT', wallet_address TEXT DEFAULT '', total_earned REAL DEFAULT 0, pending_payout REAL DEFAULT 0, created_at TEXT DEFAULT (datetime('now')))")
        db.execute("CREATE TABLE IF NOT EXISTS referrals (id INTEGER PRIMARY KEY AUTOINCREMENT, ref_code TEXT NOT NULL, subscriber_email TEXT NOT NULL, amount_earned REAL DEFAULT 2.0, status TEXT DEFAULT 'pending', created_at TEXT DEFAULT (datetime('now')), paid_at TEXT)")
        db.commit()

init_db()

def is_pro_email(email):
    if not email: return False
    with get_db() as db:
        row = db.execute("SELECT 1 FROM pro_users WHERE email=?", (email,)).fetchone()
    return bool(row)

def activate_pro_email(email, by="admin"):
    with get_db() as db:
        db.execute("INSERT OR IGNORE INTO pro_users (email, activated_by) VALUES (?,?)", (email, by))
        db.execute("UPDATE payments SET status='activated', activated_at=datetime('now') WHERE email=? AND status='pending'", (email,))
        db.commit()

def save_payment(email, method, amount="", tx_ref="", coin="", status="pending"):
    with get_db() as db:
        db.execute("INSERT INTO payments (email,method,amount,tx_ref,coin,status) VALUES (?,?,?,?,?,?)",
                   (email, method, amount, tx_ref, coin, status))
        db.commit()

# --- Credit balance helpers -------------------------------------------------
def get_credit_balance(email):
    if not email:
        return 0
    with get_db() as db:
        row = db.execute("SELECT balance FROM credits WHERE email=?", (email,)).fetchone()
    return row["balance"] if row else 0

def add_credits(email, ads):
    with get_db() as db:
        db.execute("INSERT INTO credits (email, balance) VALUES (?, ?) "
                   "ON CONFLICT(email) DO UPDATE SET balance = balance + ?",
                   (email, ads, ads))
        db.commit()

def deduct_credit(email):
    with get_db() as db:
        row = db.execute("SELECT balance FROM credits WHERE email=?", (email,)).fetchone()
        if not row or row["balance"] <= 0:
            return False
        db.execute("UPDATE credits SET balance = balance - 1 WHERE email=?", (email,))
        db.commit()
    return True

def save_credit_purchase(email, package, ads, amount_usd, amount_local, method, tx_ref="", status="pending", ref_code=""):
    with get_db() as db:
        db.execute("INSERT INTO credit_purchases (email,package,ads,amount_usd,amount_local,method,tx_ref,status) "
                   "VALUES (?,?,?,?,?,?,?,?)",
                   (email, package, ads, amount_usd, amount_local, method, tx_ref, status))
        db.execute("UPDATE credit_purchases SET ref_code=? WHERE id=last_insert_rowid()", (ref_code,))
        db.commit()

def activate_credit_purchase(tx_ref):
    """Mark a pending credit_purchases row as activated and credit the user."""
    with get_db() as db:
        row = db.execute("SELECT * FROM credit_purchases WHERE tx_ref=? AND status='pending'", (tx_ref,)).fetchone()
        if not row:
            return None
        add_credits(row["email"], row["ads"])
        if row["ref_code"]:
            commission = round(row["amount_usd"] * 0.4, 2)
            record_referral(row["ref_code"], row["email"], commission, tx_ref)
        db.execute("UPDATE credit_purchases SET status='activated', activated_at=datetime('now') WHERE id=?", (row["id"],))
        db.commit()
    return dict(row)


def get_fingerprint():
    ip = request.headers.get("X-Forwarded-For", request.remote_addr or "unknown")
    ua = request.headers.get("User-Agent", "")
    return hashlib.md5((ip + ua).encode()).hexdigest()

def get_week_start():
    today = datetime.now()
    monday = today - timedelta(days=today.weekday())
    return monday.strftime("%Y-%m-%d")

def get_free_usage():
    fp = get_fingerprint()
    week = get_week_start()
    with get_db() as db:
        row = db.execute("SELECT * FROM free_usage WHERE fingerprint=?", (fp,)).fetchone()
        if not row:
            db.execute("INSERT INTO free_usage (fingerprint, count, week_start) VALUES (?,0,?)", (fp, week))
            db.commit()
            return 0
        if row["week_start"] != week:
            db.execute("UPDATE free_usage SET count=0, week_start=? WHERE fingerprint=?", (week, fp))
            db.commit()
            return 0
        return row["count"]

def increment_free_usage():
    fp = get_fingerprint()
    week = get_week_start()
    with get_db() as db:
        db.execute("INSERT INTO free_usage (fingerprint, count, week_start) VALUES (?,1,?) ON CONFLICT(fingerprint) DO UPDATE SET count=count+1, week_start=?", (fp, week, week))
        db.commit()

def make_ref_code(name):
    base = name.upper().replace(" ","")[:6]
    suffix = hashlib.md5(str(time.time()).encode()).hexdigest()[:4].upper()
    return base + suffix

def get_permanent_ref_code(email):
    with get_db() as db:
        row = db.execute("SELECT ref_code FROM customer_referrals WHERE email=?", (email,)).fetchone()
        return row["ref_code"] if row else None

def resolve_ref_code(email):
    permanent = get_permanent_ref_code(email)
    if permanent:
        return permanent
    session_ref = session.get('ref_code', '')
    if session_ref:
        with get_db() as db:
            db.execute("INSERT INTO customer_referrals (email, ref_code) VALUES (?,?) ON CONFLICT(email) DO NOTHING", (email, session_ref))
            db.commit()
        return session_ref
    return ''

def record_referral(ref_code, subscriber_email, amount, tx_ref):
    with get_db() as db:
        existing = db.execute("SELECT 1 FROM referrals WHERE tx_ref=?", (tx_ref,)).fetchone()
        if not existing and ref_code:
            db.execute("INSERT INTO referrals (ref_code, subscriber_email, amount_earned, tx_ref) VALUES (?,?,?,?)", (ref_code, subscriber_email, amount, tx_ref))
            db.execute("UPDATE affiliates SET total_earned=total_earned+?, pending_payout=pending_payout+? WHERE ref_code=?", (amount, amount, ref_code))
            db.commit()

def make_ref():
    return "cs_" + hashlib.sha256(str(time.time()).encode()).hexdigest()[:16]

def paystack_init(email, amount_kobo, ref):
    r = requests.post("https://api.paystack.co/transaction/initialize",
        headers={"Authorization": f"Bearer {PAYSTACK_SECRET}", "Content-Type": "application/json"},
        json={"email": email, "amount": amount_kobo, "reference": ref,
              "callback_url": os.environ.get("APP_URL", "") + "/verify-paystack"})
    return r.json()

def paystack_verify(ref):
    r = requests.get(f"https://api.paystack.co/transaction/verify/{ref}",
        headers={"Authorization": f"Bearer {PAYSTACK_SECRET}"})
    return r.json()

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("admin_logged_in"):
            return redirect("/admin/login")
        return f(*args, **kwargs)
    return decorated

HTML = """<!DOCTYPE html>
<html lang="en"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>CopySwift AI</title>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&family=Inter:wght@400;500&display=swap" rel="stylesheet">
<style>
*{box-sizing:border-box;margin:0;padding:0}
:root{--bg:#060912;--surface:#0d1424;--surface2:#111827;--border:#1e2d45;--accent:#00d4ff;--accent2:#7c3aed;--gold:#f59e0b;--text:#e2e8f0;--muted:#64748b;--success:#10b981;--danger:#ef4444}
body{font-family:'Inter',sans-serif;background:var(--bg);color:var(--text);min-height:100vh;padding:20px 16px 80px}
.header{text-align:center;padding:36px 0 28px;max-width:540px;margin:0 auto}
.badge{display:inline-flex;align-items:center;gap:6px;background:rgba(0,212,255,.08);border:1px solid rgba(0,212,255,.2);color:var(--accent);font-family:'Space Grotesk',sans-serif;font-size:11px;font-weight:600;letter-spacing:.12em;text-transform:uppercase;padding:6px 14px;border-radius:100px;margin-bottom:18px}
h1{font-family:'Space Grotesk',sans-serif;font-size:clamp(26px,7vw,40px);font-weight:700;line-height:1.1;letter-spacing:-.03em;margin-bottom:10px}
h1 span{background:linear-gradient(135deg,var(--accent),var(--accent2));-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
.subtitle{color:var(--muted);font-size:14px;line-height:1.6}
.usage-bar{max-width:540px;margin:0 auto 20px;background:var(--surface);border:1px solid var(--border);border-radius:14px;padding:12px 18px;display:flex;align-items:center;justify-content:space-between;gap:12px}
.usage-label{font-size:13px;color:var(--muted);font-weight:500}
.usage-dots{display:flex;gap:6px}
.dot{width:10px;height:10px;border-radius:50%;background:var(--border)}
.dot.used{background:var(--accent);box-shadow:0 0 8px var(--accent)}
.dot.pro{background:var(--gold);box-shadow:0 0 8px var(--gold)}
.upgrade-link{font-size:12px;color:var(--gold);font-weight:600;text-decoration:none}
.card{background:var(--surface);border:1px solid var(--border);border-radius:20px;padding:26px 22px;max-width:540px;margin:0 auto 20px}
label{display:block;font-size:11px;font-weight:600;color:var(--muted);text-transform:uppercase;letter-spacing:.08em;margin-bottom:7px}
input[type=text],input[type=email]{width:100%;padding:12px 15px;background:var(--surface2);border:1px solid var(--border);border-radius:10px;color:var(--text);font-size:15px;font-family:'Inter',sans-serif;margin-bottom:16px;outline:none;transition:border-color .2s}
input[type=text]:focus,input[type=email]:focus{border-color:var(--accent)}
input[type=text]::placeholder,input[type=email]::placeholder{color:var(--muted)}
.copy-type-grid{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:20px}
.copy-type-btn{padding:10px 9px;background:var(--surface2);border:1px solid var(--border);border-radius:10px;color:var(--muted);font-size:13px;cursor:pointer;text-align:center;transition:all .2s}
.copy-type-btn.selected{background:rgba(0,212,255,.08);border-color:var(--accent);color:var(--accent);font-weight:500}
input[type=hidden]{display:none}
.generate-btn{width:100%;padding:15px;background:linear-gradient(135deg,var(--accent),var(--accent2));color:#fff;font-family:'Space Grotesk',sans-serif;font-size:16px;font-weight:700;border:none;border-radius:12px;cursor:pointer}
.generate-btn:disabled{opacity:.5;cursor:not-allowed}
.result-card{background:var(--surface);border:1px solid var(--border);border-radius:20px;padding:22px;max-width:540px;margin:0 auto 20px}
.result-header{display:flex;align-items:center;justify-content:space-between;margin-bottom:14px}
.result-label{font-family:'Space Grotesk',sans-serif;font-size:13px;font-weight:600;color:var(--accent);text-transform:uppercase;letter-spacing:.1em}
.copy-btn{padding:7px 14px;background:rgba(0,212,255,.1);border:1px solid rgba(0,212,255,.3);border-radius:8px;color:var(--accent);font-size:13px;font-weight:600;cursor:pointer}
.result-text{font-size:15px;line-height:1.75;color:var(--text);white-space:pre-wrap;word-break:break-word}
.paywall{max-width:540px;margin:0 auto 20px}
.paywall-header{background:linear-gradient(135deg,rgba(124,58,237,.2),rgba(245,158,11,.1));border:1px solid rgba(124,58,237,.35);border-radius:20px;padding:28px 22px;text-align:center;margin-bottom:16px}
.paywall-header h2{font-family:'Space Grotesk',sans-serif;font-size:22px;font-weight:700;margin-bottom:8px}
.paywall-header p{color:var(--muted);font-size:13px;line-height:1.6}
.pay-grid{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:12px}
.pay-method{background:var(--surface);border:1px solid var(--border);border-radius:16px;padding:18px 14px;text-align:center;cursor:pointer;transition:all .25s;text-decoration:none;display:block}
.pay-method:hover{border-color:var(--accent);transform:translateY(-2px)}
.pay-method.crypto-method{grid-column:1/-1}
.pay-icon{font-size:28px;margin-bottom:8px}
.pay-title{font-family:'Space Grotesk',sans-serif;font-size:14px;font-weight:700;color:var(--text);margin-bottom:4px}
.pay-sub{font-size:12px;color:var(--muted)}
.pay-badge{display:inline-block;font-size:10px;font-weight:600;padding:2px 8px;border-radius:100px;margin-top:6px}
.badge-green{background:rgba(16,185,129,.15);color:var(--success);border:1px solid rgba(16,185,129,.3)}
.badge-gold{background:rgba(245,158,11,.1);color:var(--gold);border:1px solid rgba(245,158,11,.3)}
.modal-overlay{display:none;position:fixed;inset:0;background:rgba(0,0,0,.75);z-index:100;align-items:center;justify-content:center;padding:16px}
.modal-overlay.open{display:flex}
.modal{background:var(--surface);border:1px solid var(--border);border-radius:20px;padding:26px 22px;max-width:440px;width:100%;position:relative;max-height:90vh;overflow-y:auto}
.modal-close{position:absolute;top:14px;right:16px;background:none;border:none;color:var(--muted);font-size:20px;cursor:pointer}
.modal h3{font-family:'Space Grotesk',sans-serif;font-size:18px;font-weight:700;margin-bottom:6px}
.modal p{color:var(--muted);font-size:13px;margin-bottom:18px;line-height:1.5}
.coin-tabs{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:18px}
.coin-tab{padding:8px 14px;background:var(--surface2);border:1px solid var(--border);border-radius:8px;color:var(--muted);font-size:13px;font-weight:600;cursor:pointer;transition:all .2s}
.coin-tab.active{background:rgba(0,212,255,.1);border-color:var(--accent);color:var(--accent)}
.coin-detail{display:none}
.coin-detail.active{display:block}
.wallet-box{background:var(--surface2);border:1px solid var(--border);border-radius:12px;padding:14px 16px;margin-bottom:12px;word-break:break-all}
.wallet-label{font-size:11px;color:var(--muted);font-weight:600;text-transform:uppercase;letter-spacing:.08em;margin-bottom:6px}
.wallet-addr{font-size:13px;color:var(--accent);font-family:monospace;line-height:1.5}
.wallet-network{font-size:11px;color:var(--gold);margin-top:4px}
.wallet-amount{font-size:20px;font-weight:700;color:var(--success);margin:12px 0 6px;font-family:'Space Grotesk',sans-serif}
.copy-addr-btn{width:100%;padding:11px;background:rgba(0,212,255,.1);border:1px solid rgba(0,212,255,.3);border-radius:10px;color:var(--accent);font-weight:600;font-size:14px;cursor:pointer;margin-bottom:10px}
.confirm-notice{background:rgba(16,185,129,.08);border:1px solid rgba(16,185,129,.2);border-radius:10px;padding:12px 14px;font-size:12px;color:#6ee7b7;line-height:1.5;margin-bottom:14px}
.confirm-btn{width:100%;padding:13px;background:linear-gradient(135deg,var(--success),#059669);color:#fff;font-family:'Space Grotesk',sans-serif;font-size:15px;font-weight:700;border:none;border-radius:10px;cursor:pointer}
.promo-row{display:flex;gap:8px;margin-top:10px}
.promo-row input{margin-bottom:0;flex:1}
.promo-apply{padding:12px 18px;background:var(--surface2);border:1px solid var(--border);border-radius:10px;color:var(--text);font-weight:600;font-size:14px;cursor:pointer}
.success-banner{background:rgba(16,185,129,.1);border:1px solid rgba(16,185,129,.3);border-radius:14px;padding:16px 18px;max-width:540px;margin:0 auto 20px;display:flex;align-items:center;gap:12px}
.success-banner p{font-size:14px;color:#6ee7b7;line-height:1.5}
.features{max-width:540px;margin:0 auto;display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px}
.feature{background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:14px;text-align:center}
.feature-icon{font-size:20px;margin-bottom:6px}
.feature-title{font-size:12px;font-weight:600;color:var(--text);margin-bottom:3px}
.feature-desc{font-size:11px;color:var(--muted);line-height:1.4}
.error{background:rgba(239,68,68,.1);border:1px solid rgba(239,68,68,.3);border-radius:10px;padding:12px 15px;color:#fca5a5;font-size:13px;margin-bottom:14px}
@media(max-width:400px){.copy-type-grid{grid-template-columns:1fr}.features{grid-template-columns:1fr}.pay-grid{grid-template-columns:1fr}}
</style></head><body>
<div class="header">
  <div class="badge">⚡ AI Copywriter</div>
  <h1>Write Ads That<br><span>Actually Sell</span></h1>
  <p class="subtitle">High-converting copy for your business in seconds.</p>
</div>
<div class="usage-bar">
  <span class="usage-label">{% if credits_balance > 0 %}✅ Credits available{% else %}No credits remaining{% endif %}</span>
  <div class="usage-dots">
    <span style="font-family:'Space Grotesk',sans-serif;font-size:18px;font-weight:700;color:var(--accent)">{{ credits_balance }}</span>
    <span style="color:var(--muted);font-size:12px;margin-left:4px">ad{{ 's' if credits_balance != 1 else '' }} left</span>
  </div>
  <a href="#upgrade" class="upgrade-link">Buy Credits →</a>
</div>
{% if credits_balance > 0 %}
<div class="success-banner"><span>🎉</span><p><strong>{{ credits_balance }} ad credit{{ 's' if credits_balance != 1 else '' }} available.</strong> Generate away!</p></div>
{% endif %}
{% if limit_reached %}
<div class="paywall" id="upgrade">
  <div class="paywall-header">
    <div style="font-size:36px;margin-bottom:10px">🔒</div>
    <h2>Buy Ad Credits</h2>
    <p>Pay once, generate ads as you go — no subscription needed.</p>
  </div>
  <div class="pay-grid">
    <a href="/pay-paystack?package=mini" class="pay-method">
      <div class="pay-icon">🔹</div><div class="pay-title">{{ credit_packages.mini.label }} Package</div>
      <div class="pay-sub">{{ credit_packages.mini.ads }} ad generations</div>
      <span class="pay-badge badge-green">${{ credit_packages.mini.usd }} · Card / Bank / MoMo PSB</span>
      <span class="pay-badge badge-gold" style="margin-top:6px;cursor:pointer" onclick="event.preventDefault();event.stopPropagation();openCryptoModal('mini')">💎 Or pay with crypto</span>
    </a>
    <a href="/pay-paystack?package=starter" class="pay-method">
      <div class="pay-icon">⭐</div><div class="pay-title">{{ credit_packages.starter.label }} Package</div>
      <div class="pay-sub">{{ credit_packages.starter.ads }} ad generations</div>
      <span class="pay-badge badge-green">${{ credit_packages.starter.usd }} · Card / Bank / MoMo PSB</span>
      <span class="pay-badge badge-gold" style="margin-top:6px;cursor:pointer" onclick="event.preventDefault();event.stopPropagation();openCryptoModal('starter')">💎 Or pay with crypto</span>
    </a>
    <a href="/pay-paystack?package=pro" class="pay-method">
      <div class="pay-icon">💎</div><div class="pay-title">{{ credit_packages.pro.label }} Package</div>
      <div class="pay-sub">{{ credit_packages.pro.ads }} ad generations</div>
      <span class="pay-badge badge-green">${{ credit_packages.pro.usd }} · Card / Bank / MoMo PSB</span>
      <span class="pay-badge badge-gold" style="margin-top:6px;cursor:pointer" onclick="event.preventDefault();event.stopPropagation();openCryptoModal('pro')">💎 Or pay with crypto</span>
    </a>
    <a href="/pay-paystack?package=basic" class="pay-method">
      <div class="pay-icon">⚡</div><div class="pay-title">{{ credit_packages.basic.label }} Package</div>
      <div class="pay-sub">{{ credit_packages.basic.ads }} ad generations</div>
      <span class="pay-badge badge-green">${{ credit_packages.basic.usd }} · Card / Bank / MoMo PSB</span>
      <span class="pay-badge badge-gold" style="margin-top:6px;cursor:pointer" onclick="event.preventDefault();event.stopPropagation();openCryptoModal('basic')">💎 Or pay with crypto</span>
    </a>
    <a href="/pay-paystack?package=elite" class="pay-method">
      <div class="pay-icon">🚀</div><div class="pay-title">{{ credit_packages.elite.label }} Package</div>
      <div class="pay-sub">{{ credit_packages.elite.ads }} ad generations</div>
      <span class="pay-badge badge-green">${{ credit_packages.elite.usd }} · Card / Bank / MoMo PSB</span>
      <span class="pay-badge badge-gold" style="margin-top:6px;cursor:pointer" onclick="event.preventDefault();event.stopPropagation();openCryptoModal('elite')">💎 Or pay with crypto</span>
    </a>
  </div>
  <div class="card" style="margin-top:0">
    <label>Have a promo code?</label>
    <form method="POST" action="/promo">
      <div class="promo-row">
        <input type="text" name="code" placeholder="Enter promo code" style="margin-bottom:0">
        <button type="submit" class="promo-apply">Apply</button>
      </div>
      {% if promo_error %}<div class="error" style="margin-top:10px">{{ promo_error }}</div>{% endif %}
    </form>
  </div>
  <a href="/reset" style="display:block;text-align:center;color:var(--muted);font-size:13px;margin-top:6px;text-decoration:none">Start new free session</a>
</div>
<div class="modal-overlay" id="cryptoModal">
  <div class="modal">
    <button class="modal-close" onclick="closeCryptoModal()">✕</button>
    <h3>💰 Pay with Crypto</h3>
    <p id="cryptoPkgLabel">Choose a coin, send the exact amount, then submit your TX hash below.</p>
    <div class="coin-tabs">
      {% for coin, info in crypto_wallets.items() %}
      <div class="coin-tab {% if loop.first %}active{% endif %}" onclick="selectCoin('{{ coin }}')">{{ info.icon }} {{ coin }}</div>
      {% endfor %}
    </div>
    {% for coin, info in crypto_wallets.items() %}
    <div class="coin-detail {% if loop.first %}active{% endif %}" id="coin-{{ coin }}" data-rate="{{ info.rate }}">
      <div class="wallet-amount" id="amount-{{ coin }}">— {{ coin }}</div>
      <div class="wallet-box">
        <div class="wallet-label">{{ coin }} Wallet Address</div>
        <div class="wallet-addr" id="addr-{{ coin }}">{{ info.address }}</div>
        <div class="wallet-network">📡 Network: {{ info.network }}</div>
      </div>
      <button class="copy-addr-btn" onclick="copyAddr('{{ coin }}')">📋 Copy {{ coin }} Address</button>
    </div>
    {% endfor %}
    <div class="confirm-notice">⚠️ Send only on the correct network. After sending, paste your TX hash and email below.</div>
    <form method="POST" action="/confirm-crypto">
      <label>Your email</label>
      <input type="email" name="email" placeholder="you@email.com" required>
      <label>Transaction Hash</label>
      <input type="text" name="tx_hash" placeholder="0xabc123..." required>
      <input type="hidden" name="coin" id="selected_coin_input" value="{{ crypto_wallets.keys()|list|first }}">
      <input type="hidden" name="package" id="selected_package_input" value="mini">
      <button type="submit" class="confirm-btn" id="cryptoConfirmBtn">✅ I've Sent Payment</button>
    </form>
  </div>
</div>
{% else %}
<div class="card">
  {% if error %}<div class="error">⚠️ {{ error }}</div>{% endif %}
  <form method="POST" id="copyForm">
    <label>Your email</label>
    <input type="email" name="email" placeholder="you@email.com" required value="{{ user_email or '' }}">
    <label>What are you selling?</label>
    <input type="text" name="product" placeholder="e.g. Skin glow cream, Online course..." required value="{{ product or '' }}">
    <label>Who is your buyer?</label>
    <input type="text" name="audience" placeholder="e.g. Nigerian women, Young entrepreneurs..." value="{{ audience or '' }}">
    <label>Type of copy</label>
    <div class="copy-type-grid">
      {% for key, val in copy_types.items() %}
      <div class="copy-type-btn {% if selected_type == key %}selected{% endif %}" onclick="selectType('{{ key }}',this)">{{ val.label }}</div>
      {% endfor %}
    </div>
    <input type="hidden" name="copy_type" id="copy_type_input" value="{{ selected_type or 'ad' }}">
    <button type="submit" class="generate-btn" id="genBtn">⚡ Generate Copy ({{ credits_balance }} left)</button>
  </form>
</div>
{% if result %}
<div class="result-card">
  <div class="result-header">
    <span class="result-label">✅ Your Copy</span>
    <button class="copy-btn" onclick="copyResult()">📋 Copy</button>
  </div>
  <div class="result-text" id="resultText">{{ result }}</div>
</div>
<div class="image-gen-card" style="background:#1a1a2e;border:1px solid #00d4ff33;border-radius:16px;padding:20px;margin:20px 0">
  <div style="font-size:15px;font-weight:700;color:#00d4ff;margin-bottom:8px">🎨 Generate Ad Image (2 credits)</div>
  <div style="font-size:12px;color:#888;margin-bottom:12px">Powered by FLUX.1 AI — describe your ideal ad image</div>
  <textarea id="imgPrompt" placeholder="e.g. A modern Nigerian woman using a smartphone app, vibrant colors, professional ad style" style="width:100%;padding:12px;background:#0d0d1a;border:1px solid #333;border-radius:10px;color:#fff;font-size:13px;resize:vertical;min-height:80px;box-sizing:border-box"></textarea>
  <button onclick="generateImage()" id="imgBtn" style="width:100%;margin-top:10px;padding:13px;background:linear-gradient(135deg,#7c3aed,#00d4ff);color:#fff;font-weight:700;font-size:15px;border:none;border-radius:10px;cursor:pointer">🖼️ Generate Image</button>
  <div id="imgStatus" style="text-align:center;color:#888;font-size:13px;margin-top:10px;display:none">⏳ Generating image, please wait 15-30 seconds...</div>
  <div id="imgResult" style="margin-top:15px;display:none">
    <img id="generatedImg" src="" style="width:100%;border-radius:12px;border:1px solid #00d4ff44" />
    <a id="imgDownload" href="" download="copyswift-ad.png" target="_blank" style="display:block;text-align:center;margin-top:10px;color:#00d4ff;font-size:13px">⬇️ Download Image</a>
  </div>
  <div id="imgError" style="color:#ff4444;font-size:13px;margin-top:10px;display:none"></div>
</div>
{% endif %}
{% endif %}
<div class="features">
  <div class="feature"><div class="feature-icon">📣</div><div class="feature-title">6 Copy Types</div><div class="feature-desc">Ads, email, WhatsApp & more</div></div>
  <div class="feature"><div class="feature-icon">⚡</div><div class="feature-title">Instant AI</div><div class="feature-desc">Results in 5 seconds</div></div>
  <div class="feature"><div class="feature-icon">🌍</div><div class="feature-title">Any Market</div><div class="feature-desc">African & global use</div></div>
</div>
<div style="text-align:center;font-size:13px;color:#888;margin:20px 0">Need help? Email <a href="mailto:supportcopyswiftai@gmail.com" style="color:#00d4ff">supportcopyswiftai@gmail.com</a></div>
<script>
function selectType(key,el){document.querySelectorAll('.copy-type-btn').forEach(b=>b.classList.remove('selected'));el.classList.add('selected');document.getElementById('copy_type_input').value=key}
function copyResult(){const t=document.getElementById('resultText').innerText;navigator.clipboard.writeText(t).then(()=>{const b=document.querySelector('.copy-btn');b.textContent='✅ Copied!';setTimeout(()=>b.textContent='📋 Copy',2000)})}
async function generateImage(){
  const prompt=document.getElementById('imgPrompt').value.trim();
  if(!prompt){alert('Please enter an image description first.');return;}
  const btn=document.getElementById('imgBtn');
  const status=document.getElementById('imgStatus');
  const result=document.getElementById('imgResult');
  const errDiv=document.getElementById('imgError');
  btn.disabled=true;btn.textContent='⏳ Generating...';
  status.style.display='block';result.style.display='none';errDiv.style.display='none';
  try{
    const resp=await fetch('/api/generate-image',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({prompt:prompt})});
    const data=await resp.json();
    if(data.image_url){
      document.getElementById('generatedImg').src=data.image_url;
      document.getElementById('imgDownload').href=data.image_url;
      result.style.display='block';
      status.style.display='none';
    }else{
      errDiv.textContent=data.error||'Image generation failed.';
      errDiv.style.display='block';status.style.display='none';
    }
  }catch(e){
    errDiv.textContent='Network error. Please try again.';
    errDiv.style.display='block';status.style.display='none';
  }
  btn.disabled=false;btn.textContent='🖼️ Generate Image';
}
document.getElementById('copyForm')?.addEventListener('submit',function(){const b=document.getElementById('genBtn');b.disabled=true;b.textContent='⚡ Generating...'})
const PACKAGES = {{ credit_packages|tojson }};
function openCryptoModal(pkgId){
  if(pkgId && PACKAGES[pkgId]) window.currentCryptoPackage = pkgId;
  if(!window.currentCryptoPackage) window.currentCryptoPackage = 'mini';
  const pkg = PACKAGES[window.currentCryptoPackage];
  document.getElementById('selected_package_input').value = window.currentCryptoPackage;
  document.getElementById('cryptoPkgLabel').textContent = 'Paying for ' + pkg.label + ' Package ($' + pkg.usd + ') — choose a coin, send the exact amount, then submit your TX hash below.';
  document.getElementById('cryptoConfirmBtn').textContent = "✅ I've Sent Payment — Activate " + pkg.label;
  document.querySelectorAll('.coin-detail').forEach(function(el){
    const coin = el.id.replace('coin-','');
    const rate = parseFloat(el.dataset.rate);
    const amt = Math.round(rate * pkg.usd * 10000) / 10000;
    document.getElementById('amount-'+coin).textContent = amt + ' ' + coin + ' ≈ $' + pkg.usd;
  });
  document.getElementById('cryptoModal').classList.add('open');
}
function closeCryptoModal(){document.getElementById('cryptoModal').classList.remove('open')}
function selectCoin(coin){document.querySelectorAll('.coin-tab').forEach(t=>t.classList.remove('active'));document.querySelectorAll('.coin-detail').forEach(d=>d.classList.remove('active'));event.target.classList.add('active');document.getElementById('coin-'+coin).classList.add('active');document.getElementById('selected_coin_input').value=coin}
function copyAddr(coin){const addr=document.getElementById('addr-'+coin).innerText;navigator.clipboard.writeText(addr).then(()=>{const b=event.target;b.textContent='✅ Copied!';setTimeout(()=>b.textContent='📋 Copy '+coin+' Address',2000)})}

document.getElementById('cryptoModal')?.addEventListener('click',e=>{if(e.target===document.getElementById('cryptoModal'))closeCryptoModal()})
</script>
</body></html>"""

ADMIN_LOGIN_HTML = """<!DOCTYPE html><html lang="en"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Admin Login</title>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@600;700&family=Inter:wght@400&display=swap" rel="stylesheet">
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Inter',sans-serif;background:#060912;color:#e2e8f0;min-height:100vh;display:flex;align-items:center;justify-content:center;padding:20px}
.card{background:#0d1424;border:1px solid #1e2d45;border-radius:20px;padding:36px 28px;max-width:380px;width:100%;text-align:center}
h2{font-family:'Space Grotesk',sans-serif;font-size:22px;font-weight:700;margin-bottom:6px}
p{color:#64748b;font-size:13px;margin-bottom:24px}
input{width:100%;padding:13px 15px;background:#111827;border:1px solid #1e2d45;border-radius:10px;color:#e2e8f0;font-size:15px;outline:none;margin-bottom:14px}
input:focus{border-color:#00d4ff}
button{width:100%;padding:14px;background:linear-gradient(135deg,#00d4ff,#7c3aed);color:#fff;font-family:'Space Grotesk',sans-serif;font-size:16px;font-weight:700;border:none;border-radius:12px;cursor:pointer}
.err{background:rgba(239,68,68,.1);border:1px solid rgba(239,68,68,.3);border-radius:8px;padding:10px;color:#fca5a5;font-size:13px;margin-bottom:14px}
</style></head><body>
<div class="card">
  <div style="font-size:40px;margin-bottom:14px">🛡️</div>
  <h2>Admin Login</h2><p>CopySwift AI Dashboard</p>
  {% if error %}<div class="err">{{ error }}</div>{% endif %}
  <form method="POST">
    <input type="password" name="password" placeholder="Admin password" required autofocus>
    <button type="submit">Login →</button>
  </form>
</div></body></html>"""

ADMIN_HTML = """<!DOCTYPE html><html lang="en"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>CopySwift Admin</title>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500&display=swap" rel="stylesheet">
<style>
*{box-sizing:border-box;margin:0;padding:0}
:root{--bg:#060912;--surface:#0d1424;--surface2:#111827;--border:#1e2d45;--accent:#00d4ff;--accent2:#7c3aed;--gold:#f59e0b;--text:#e2e8f0;--muted:#64748b;--success:#10b981;--danger:#ef4444}
body{font-family:'Inter',sans-serif;background:var(--bg);color:var(--text);min-height:100vh}
.layout{display:flex;min-height:100vh}
.sidebar{width:220px;background:var(--surface);border-right:1px solid var(--border);padding:24px 0;flex-shrink:0;position:fixed;top:0;left:0;height:100vh;overflow-y:auto}
.sidebar-logo{padding:0 20px 24px;border-bottom:1px solid var(--border);margin-bottom:16px}
.sidebar-logo h2{font-family:'Space Grotesk',sans-serif;font-size:16px;font-weight:700;color:var(--accent)}
.sidebar-logo p{font-size:11px;color:var(--muted);margin-top:2px}
.nav-item{display:block;padding:10px 20px;color:var(--muted);font-size:13px;font-weight:500;text-decoration:none;transition:all .2s;border-left:3px solid transparent}
.nav-item:hover,.nav-item.active{color:var(--text);background:rgba(0,212,255,.05);border-left-color:var(--accent)}
.nav-section{padding:16px 20px 6px;font-size:10px;font-weight:600;color:var(--muted);text-transform:uppercase;letter-spacing:.1em}
.main{margin-left:220px;padding:28px 24px;flex:1}
.stats-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:16px;margin-bottom:28px}
.stat-card{background:var(--surface);border:1px solid var(--border);border-radius:16px;padding:20px 18px}
.stat-label{font-size:11px;color:var(--muted);font-weight:600;text-transform:uppercase;letter-spacing:.08em;margin-bottom:8px}
.stat-value{font-family:'Space Grotesk',sans-serif;font-size:28px;font-weight:700;line-height:1}
.stat-sub{font-size:12px;color:var(--muted);margin-top:6px}
.section-title{font-family:'Space Grotesk',sans-serif;font-size:17px;font-weight:700;margin-bottom:16px;display:flex;align-items:center;gap:8px}
.table-wrap{background:var(--surface);border:1px solid var(--border);border-radius:16px;overflow:hidden;margin-bottom:28px;overflow-x:auto}
table{width:100%;border-collapse:collapse}
th{padding:12px 16px;text-align:left;font-size:11px;font-weight:600;color:var(--muted);text-transform:uppercase;letter-spacing:.07em;background:var(--surface2);border-bottom:1px solid var(--border)}
td{padding:13px 16px;font-size:13px;border-bottom:1px solid var(--border)}
tr:last-child td{border-bottom:none}
.status{display:inline-block;padding:3px 10px;border-radius:100px;font-size:11px;font-weight:600}
.status.pending{background:rgba(245,158,11,.12);color:var(--gold);border:1px solid rgba(245,158,11,.3)}
.status.activated{background:rgba(16,185,129,.12);color:var(--success);border:1px solid rgba(16,185,129,.3)}
.status.rejected{background:rgba(239,68,68,.12);color:var(--danger);border:1px solid rgba(239,68,68,.3)}
.status.paid{background:rgba(16,185,129,.12);color:var(--success);border:1px solid rgba(16,185,129,.3)}
.btn-small{padding:6px 14px;font-size:12px;font-weight:600;background:var(--primary,#6366f1);color:#fff;border:none;border-radius:6px;cursor:pointer}
.btn-small:hover{opacity:.85}
.btn{padding:6px 14px;border-radius:8px;font-size:12px;font-weight:600;cursor:pointer;border:none;transition:all .2s}
.btn-activate{background:rgba(16,185,129,.15);color:var(--success);border:1px solid rgba(16,185,129,.3)}
.btn-reject{background:rgba(239,68,68,.1);color:var(--danger);border:1px solid rgba(239,68,68,.3)}
.btn-primary{background:linear-gradient(135deg,var(--accent),var(--accent2));color:#fff;padding:10px 20px;border-radius:10px;font-size:13px;border:none;cursor:pointer;font-weight:600}
.manual-card{background:var(--surface);border:1px solid var(--border);border-radius:16px;padding:22px;margin-bottom:28px}
.manual-card h3{font-family:'Space Grotesk',sans-serif;font-size:15px;font-weight:700;margin-bottom:14px}
.input-row{display:flex;gap:10px}
.input-row input{flex:1;padding:10px 14px;background:var(--surface2);border:1px solid var(--border);border-radius:10px;color:var(--text);font-size:14px;outline:none}
.input-row input:focus{border-color:var(--accent)}
.toast{position:fixed;bottom:24px;right:24px;background:#10b981;color:#fff;padding:12px 20px;border-radius:12px;font-weight:600;font-size:14px;display:none;z-index:999}
.toast.show{display:block}
.logout{display:block;padding:10px 20px;color:var(--danger);font-size:13px;font-weight:500;text-decoration:none;margin-top:16px;border-top:1px solid var(--border);padding-top:16px}
.tx{font-family:monospace;font-size:11px;color:var(--accent);max-width:120px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;cursor:pointer;display:block}
@media(max-width:700px){.sidebar{width:100%;height:auto;position:relative}.main{margin-left:0}.layout{flex-direction:column}}
</style></head><body>
<div class="layout">
  <div class="sidebar">
    <div class="sidebar-logo"><h2>⚡ CopySwift</h2><p>Admin Dashboard</p></div>
    <span class="nav-section">Overview</span>
    <a class="nav-item active" href="/admin">📊 Dashboard</a>
    <span class="nav-section">Payments</span>
    <a class="nav-item" href="/admin#pending">⏳ Pending ({{ pending_count }})</a>
    <a class="nav-item" href="/admin#all">📋 All Payments</a>
    <span class="nav-section">Credits</span>
    <a class="nav-item" href="/admin#credit-purchases">🎟️ Credit Purchases ({{ stats.credit_pending }} pending)</a>
    <a class="nav-item" href="/admin#credit-balances">💰 Active Balances</a>
    <span class="nav-section">Users</span>
    <a class="nav-item" href="/admin#pro-users">✨ Pro Users</a>
    <a class="nav-item" href="/admin#manual">➕ Activate Manually</a>
    <span class="nav-section">Affiliates</span>
    <a class="nav-item" href="/admin#affiliates">🤝 Affiliates</a>
    <span class="nav-section">App</span>
    <a class="nav-item" href="/" target="_blank">🔗 View Live App</a>
    <a class="nav-item logout" href="/admin/logout">🚪 Logout</a>
  </div>
  <div class="main">
    <div style="margin-bottom:24px">
      <h1 style="font-family:'Space Grotesk',sans-serif;font-size:24px;font-weight:700">Dashboard</h1>
      <p style="color:var(--muted);font-size:13px;margin-top:4px">{{ now }}</p>
    </div>
    <div class="stats-grid">
      <div class="stat-card"><div class="stat-label">Total Payments</div><div class="stat-value" style="color:var(--accent)">{{ stats.total }}</div><div class="stat-sub">All time</div></div>
      <div class="stat-card"><div class="stat-label">Pending</div><div class="stat-value" style="color:var(--gold)">{{ stats.pending }}</div><div class="stat-sub">Need action</div></div>
      <div class="stat-card"><div class="stat-label">Activated</div><div class="stat-value" style="color:var(--success)">{{ stats.activated }}</div><div class="stat-sub">Pro users</div></div>
      <div class="stat-card"><div class="stat-label">Pro Users</div><div class="stat-value" style="color:#a78bfa">{{ stats.pro_count }}</div><div class="stat-sub">Total active</div></div>
    </div>
    <a name="credit-purchases"></a>
    <div class="section-title">🎟️ Credit Purchases</div>
    <div class="table-wrap">
      <table>
        <tr><th>Email</th><th>Package</th><th>Ads</th><th>Amount</th><th>Method</th><th>Status</th><th>Date</th></tr>
        {% for c in credit_purchases %}
        <tr>
          <td>{{ c.email }}</td>
          <td>{{ c.package|capitalize }}</td>
          <td>{{ c.ads }}</td>
          <td>${{ c.amount_usd }}</td>
          <td>{{ c.method }}</td>
          <td><span class="status {{ c.status }}">{{ c.status }}</span></td>
          <td>{{ c.created_at }}</td>
        </tr>
        {% else %}
        <tr><td colspan="7" style="text-align:center;color:var(--muted)">No credit purchases yet</td></tr>
        {% endfor %}
      </table>
    </div>
    <a name="credit-balances"></a>
    <div class="section-title">💰 Active Credit Balances</div>
    <div class="table-wrap">
      <table>
        <tr><th>Email</th><th>Credits Remaining</th></tr>
        {% for b in credit_balances %}
        <tr><td>{{ b.email }}</td><td>{{ b.balance }}</td></tr>
        {% else %}
        <tr><td colspan="2" style="text-align:center;color:var(--muted)">No active balances</td></tr>
        {% endfor %}
      </table>
    </div>
    <a name="manual"></a>
    <div class="manual-card">
      <h3>➕ Activate Pro Manually</h3>
      <p style="font-size:13px;color:var(--muted);margin-bottom:14px">Enter customer email to grant Pro access instantly.</p>
      <form method="POST" action="/admin/activate-manual">
        <select name="package" style="width:100%;padding:10px 14px;background:var(--surface2);border:1px solid var(--border);border-radius:10px;color:var(--text);font-size:14px;margin-bottom:10px">
          <option value="basic">Basic — 120 ads ($18)</option>
          <option value="elite">Elite — 180 ads ($25)</option>
        </select>
        <div class="input-row">
          <input type="email" name="email" placeholder="customer@email.com" required>
          <button type="submit" class="btn-primary">✅ Activate Pro</button>
        </div>
      </form>
    </div>
    <a name="pending"></a>
    <div class="section-title">⏳ Pending Crypto Payments <span style="background:rgba(245,158,11,.15);color:var(--gold);font-size:12px;padding:3px 10px;border-radius:100px;font-weight:600">{{ pending_count }} pending</span></div>
    <div class="table-wrap"><table>
      <tr><th>Email</th><th>Coin</th><th>TX Hash</th><th>Submitted</th><th>Actions</th></tr>
      {% if pending_payments %}{% for p in pending_payments %}
      <tr>
        <td>{{ p['email'] }}</td>
        <td><strong>{{ p['coin'] or p['method'] }}</strong></td>
        <td><span class="tx" title="{{ p['tx_ref'] }}" onclick="navigator.clipboard.writeText('{{ p['tx_ref'] }}')">{{ p['tx_ref'][:20] }}...</span></td>
        <td style="color:var(--muted)">{{ p['created_at'][:16] }}</td>
        <td>
          <form method="POST" action="/admin/activate/{{ p['id'] }}" style="display:inline">
            <button type="submit" class="btn btn-activate">✅ Activate</button>
          </form>
          <form method="POST" action="/admin/reject/{{ p['id'] }}" style="display:inline;margin-left:6px">
            <button type="submit" class="btn btn-reject">✗ Reject</button>
          </form>
        </td>
      </tr>
      {% endfor %}{% else %}
      <tr><td colspan="5" style="text-align:center;color:var(--muted);padding:24px">No pending payments 🎉</td></tr>
      {% endif %}
    </table></div>
    <a name="all"></a>
    <div class="section-title">📋 All Payments</div>
    <div class="table-wrap"><table>
      <tr><th>Email</th><th>Method</th><th>Amount</th><th>Status</th><th>Date</th></tr>
      {% if all_payments %}{% for p in all_payments %}
      <tr>
        <td>{{ p['email'] }}</td><td>{{ p['method'] }}</td>
        <td style="color:var(--success)">{{ p['amount'] or '—' }}</td>
        <td><span class="status {{ p['status'] }}">{{ p['status'] }}</span></td>
        <td style="color:var(--muted)">{{ p['created_at'][:16] }}</td>
      </tr>
      {% endfor %}{% else %}
      <tr><td colspan="5" style="text-align:center;color:var(--muted);padding:24px">No payments yet</td></tr>
      {% endif %}
    </table></div>
    <a name="pro-users"></a>
    <div class="section-title">✨ Pro Users</div>
    <div class="table-wrap"><table>
      <tr><th>Email</th><th>Activated By</th><th>Date</th></tr>
      {% if pro_users %}{% for u in pro_users %}
      <tr>
        <td><strong>{{ u['email'] }}</strong></td>
        <td style="color:var(--muted)">{{ u['activated_by'] }}</td>
        <td style="color:var(--muted)">{{ u['activated_at'][:16] }}</td>
      </tr>
      {% endfor %}{% else %}
      <tr><td colspan="3" style="text-align:center;color:var(--muted);padding:24px">No pro users yet</td></tr>
      {% endif %}
    </table></div>
    <a name="affiliates"></a>
    <div class="section-title">🤝 Affiliates</div>
    <div class="table-wrap"><table>
      <tr><th>Name</th><th>Email</th><th>Ref Code</th><th>Total Earned</th><th>Pending Payout</th><th>Action</th></tr>
      {% if affiliates %}{% for a in affiliates %}
      <tr>
        <td>{{ a['name'] }}</td>
        <td>{{ a['email'] }}</td>
        <td><code>{{ a['ref_code'] }}</code></td>
        <td style="color:var(--success)">${{ "%.2f"|format(a['total_earned']) }}</td>
        <td style="color:var(--gold)">${{ "%.2f"|format(a['pending_payout']) }}</td>
        <td>
          {% if a['pending_payout'] > 0 %}
          <button class="btn-small" onclick="markPaid({{ a['id'] }})">Mark Paid</button>
          {% else %}<span style="color:var(--muted)">—</span>{% endif %}
        </td>
      </tr>
      {% endfor %}{% else %}
      <tr><td colspan="6" style="text-align:center;color:var(--muted);padding:24px">No affiliates yet</td></tr>
      {% endif %}
    </table></div>
    <a name="referrals"></a>
    <div class="section-title">💸 Referral Commissions</div>
    <div class="table-wrap"><table>
      <tr><th>Ref Code</th><th>Customer</th><th>Amount</th><th>Status</th><th>Date</th></tr>
      {% if referrals %}{% for r in referrals %}
      <tr>
        <td><code>{{ r['ref_code'] }}</code></td>
        <td>{{ r['subscriber_email'] }}</td>
        <td style="color:var(--success)">${{ "%.2f"|format(r['amount_earned']) }}</td>
        <td><span class="status {{ r['status'] }}">{{ r['status'] }}</span></td>
        <td style="color:var(--muted)">{{ r['created_at'][:16] }}</td>
      </tr>
      {% endfor %}{% else %}
      <tr><td colspan="5" style="text-align:center;color:var(--muted);padding:24px">No referral commissions yet</td></tr>
      {% endif %}
    </table></div>
  </div>
</div>
{% if flash %}<div class="toast show" id="toast">{{ flash }}</div>
<script>setTimeout(()=>document.getElementById('toast').classList.remove('show'),3500)</script>{% endif %}
<script>
async function markPaid(affiliateId){
  if(!confirm("Mark this payout as paid?"))return;
  try{
    const resp=await fetch("/admin/mark-payout-paid",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({affiliate_id:affiliateId})});
    const data=await resp.json();
    if(data.success){alert("Payout marked as paid!");location.reload();}else{alert("Error: "+(data.error||"unknown"));}
  }catch(err){alert("Failed: "+err.message);}
}
</script>
</body></html>"""

PAYSTACK_HTML = """<!DOCTYPE html><html lang="en"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Pay — CopySwift Pro</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Inter',sans-serif;background:#060912;color:#e2e8f0;min-height:100vh;display:flex;align-items:center;justify-content:center;padding:20px}
.card{background:#0d1424;border:1px solid #1e2d45;border-radius:20px;padding:32px 26px;max-width:420px;width:100%}
h2{font-size:22px;font-weight:700;margin-bottom:8px}
p{color:#64748b;font-size:14px;margin-bottom:22px;line-height:1.6}
label{display:block;font-size:11px;font-weight:600;color:#64748b;text-transform:uppercase;letter-spacing:.08em;margin-bottom:7px}
input{width:100%;padding:13px 15px;background:#111827;border:1px solid #1e2d45;border-radius:10px;color:#e2e8f0;font-size:15px;outline:none;margin-bottom:18px}
input:focus{border-color:#00d4ff}
.pay-btn{width:100%;padding:15px;background:linear-gradient(135deg,#00c3ff,#0075ff);color:#fff;font-size:16px;font-weight:700;border:none;border-radius:12px;cursor:pointer}
.back{display:block;text-align:center;color:#64748b;font-size:13px;margin-top:14px;text-decoration:none}
.err{background:rgba(239,68,68,.1);border:1px solid rgba(239,68,68,.3);border-radius:8px;padding:10px;color:#fca5a5;font-size:13px;margin-bottom:14px}
</style></head><body>
<div class="card">
  <div style="font-size:32px;margin-bottom:12px">💳</div>
  <h2>Buy {{ pkg.label }} Package</h2>
  <p>{{ pkg.ads }} ad generations for <strong>${{ pkg.usd }}</strong> (≈ ₦{{ "{:,.0f}".format(amount_ngn) }}).<br>
  Pay securely via Card, Bank Transfer, or <strong>MoMo PSB</strong> (Mobile Money) through Paystack.</p>
  {% if error %}<div class="err">{{ error }}</div>{% endif %}
  <form method="POST">
    <input type="hidden" name="package" value="{{ package }}">
    <input type="hidden" name="ref_code" value="{{ ref_code or '' }}">
    <label>Your Email Address</label>
    <input type="email" name="email" placeholder="you@email.com" required value="{{ email or '' }}">
    <button type="submit" class="pay-btn">🔒 Pay ${{ pkg.usd }} Securely</button>
  </form>
  <a href="/" class="back">← Back to CopySwift</a>
</div></body></html>"""

PENDING_HTML = """<!DOCTYPE html><html lang="en"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Payment Submitted</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Inter',sans-serif;background:#060912;color:#e2e8f0;min-height:100vh;display:flex;align-items:center;justify-content:center;padding:20px}
.card{background:#0d1424;border:1px solid #1e2d45;border-radius:20px;padding:36px 26px;max-width:420px;width:100%;text-align:center}
h2{font-size:22px;font-weight:700;margin-bottom:10px}
p{color:#64748b;font-size:14px;line-height:1.7;margin-bottom:16px}
.home-btn{display:inline-block;padding:13px 28px;background:linear-gradient(135deg,#00d4ff,#7c3aed);color:#fff;font-weight:700;font-size:15px;border-radius:12px;text-decoration:none;margin-top:8px}
</style></head><body>
<div class="card">
  <div style="font-size:48px;margin-bottom:16px">⏳</div>
  <h2>Payment Submitted!</h2>
  <p>Your crypto payment has been received.<br><strong>{{ email }}</strong></p>
  <p>TX: <code style="color:#00d4ff;font-size:12px;word-break:break-all">{{ tx_hash }}</code></p>
  <p>Your credits activate within <strong>30–60 minutes</strong>.</p>
  <p style="font-size:13px;color:#888">Need help? Email <a href="mailto:supportcopyswiftai@gmail.com" style="color:#00d4ff">supportcopyswiftai@gmail.com</a></p>
  <a href="/" class="home-btn">Back to CopySwift</a>
</div></body></html>"""

@app.route('/', methods=['GET','POST'])
def home():
    user_email = session.get('user_email', '')
    is_admin = session.get('admin_logged_in', False)
    credits_balance = 9999 if is_admin else (get_credit_balance(user_email) if user_email else 0)
    limit_reached = False if is_admin else (credits_balance <= 0)
    result = error = product = audience = None
    selected_type = 'ad'
    ref_code = request.args.get('ref', session.get('ref_code',''))
    if ref_code: session['ref_code'] = ref_code
    if request.method == 'POST' and not limit_reached:
        form_email = request.form.get('email','').strip()
        if form_email and not user_email:
            user_email = form_email
            session['user_email'] = form_email
        if not user_email and not is_admin:
            error = "Please enter your email and purchase a credit package to generate copy."
        else:
            product = request.form.get('product','').strip()
            audience = request.form.get('audience','').strip() or 'customers'
            selected_type = request.form.get('copy_type','ad')
            if selected_type not in COPY_TYPES: selected_type = 'ad'
            prompt = COPY_TYPES[selected_type]['prompt'].format(product=product, audience=audience)
            try:
                cc = client.chat.completions.create(messages=[{"role":"user","content":prompt}], model="llama-3.1-8b-instant")
                result = cc.choices[0].message.content
                if not is_admin:
                    deduct_credit(user_email)
                    credits_balance = get_credit_balance(user_email)
                    limit_reached = (credits_balance <= 0)
            except Exception as e:
                error = str(e)
    return render_template_string(HTML, result=result, error=error, product=product, audience=audience,
        selected_type=selected_type, copy_types=COPY_TYPES,
        credits_balance=credits_balance, limit_reached=limit_reached,
        user_email=user_email, credit_packages=CREDIT_PACKAGES,
        crypto_wallets=CRYPTO_WALLETS, promo_error=None)

@app.route('/pay-paystack', methods=['GET','POST'])
def pay_paystack():
    error = email = None
    package = request.args.get('package') or request.form.get('package') or 'basic'
    if package not in CREDIT_PACKAGES:
        package = 'basic'
    pkg = CREDIT_PACKAGES[package]
    amount_kobo, amount_ngn, rate = usd_to_kobo(pkg['usd'])
    ref_code = request.args.get('ref_code', request.form.get('ref_code', session.get('ref_code','')))
    if ref_code: session['ref_code'] = ref_code
    if request.method == 'POST':
        email = request.form.get('email','').strip()
        if not PAYSTACK_SECRET:
            error = "Paystack not configured. Contact support: supportcopyswiftai@gmail.com"
        else:
            ref = make_ref()
            session['pay_ref'] = ref
            session['pay_email'] = email
            session['pay_package'] = package
            save_credit_purchase(email, package, pkg['ads'], pkg['usd'], f"₦{amount_ngn:,.2f}", "paystack", ref, ref_code=resolve_ref_code(email))
            res = paystack_init(email, amount_kobo, ref)
            if res.get('status'):
                return redirect(res['data']['authorization_url'])
            error = res.get('message','Payment init failed.')
    return render_template_string(PAYSTACK_HTML, error=error, email=email,
        package=package, pkg=pkg, amount_ngn=amount_ngn, ref_code=ref_code)

@app.route('/verify-paystack')
def verify_paystack():
    ref = request.args.get('reference') or session.get('pay_ref','')
    if ref and PAYSTACK_SECRET:
        res = paystack_verify(ref)
        if res.get('data',{}).get('status') == 'success':
            email = session.get('pay_email','')
            purchase = activate_credit_purchase(ref)
            if email:
                session['user_email'] = email
    return redirect('/')

@app.route('/confirm-crypto', methods=['POST'])
def confirm_crypto():
    email = request.form.get('email','').strip()
    tx_hash = request.form.get('tx_hash','').strip()
    coin = request.form.get('coin','').strip()
    package = request.form.get('package','mini')
    if package not in CREDIT_PACKAGES:
        package = 'mini'
    pkg = CREDIT_PACKAGES[package]
    save_payment(email, "crypto", f"${pkg['usd']} {coin}", tx_hash, coin, "pending")
    save_credit_purchase(email, package, pkg['ads'], pkg['usd'], f"{coin}", "crypto", tx_hash, "pending", ref_code=resolve_ref_code(email))
    session['user_email'] = email
    return render_template_string(PENDING_HTML, email=email, tx_hash=tx_hash)

@app.route('/promo', methods=['POST'])
def promo():
    code = request.form.get('code','').strip().upper()
    user_email = session.get('user_email', '')
    if code in PROMO_CODES and user_email:
        add_credits(user_email, CREDIT_PACKAGES['basic']['ads'])
        return redirect('/')
    credits_balance = get_credit_balance(user_email) if user_email else 0
    return render_template_string(HTML, result=None, error=None, product=None, audience=None,
        selected_type='ad', copy_types=COPY_TYPES,
        credits_balance=credits_balance, limit_reached=(credits_balance <= 0),
        user_email=user_email, credit_packages=CREDIT_PACKAGES,
        crypto_wallets=CRYPTO_WALLETS,
        promo_error="Invalid promo code, or please enter your email and generate at least once first.")

@app.route('/reset')
def reset():
    session.clear()
    return redirect('/')

@app.route('/admin/login', methods=['GET','POST'])
def admin_login():
    error = None
    if request.method == 'POST':
        if request.form.get('password') == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            return redirect('/admin')
        error = "Wrong password."
    return render_template_string(ADMIN_LOGIN_HTML, error=error)

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect('/admin/login')

@app.route('/admin')
@admin_required
def admin_dashboard():
    with get_db() as db:
        all_payments = [dict(r) for r in db.execute("SELECT * FROM payments ORDER BY created_at DESC LIMIT 100").fetchall()]
        pending_payments = [p for p in all_payments if p['status']=='pending' and p['method']=='crypto']
        pro_users = [dict(r) for r in db.execute("SELECT * FROM pro_users ORDER BY activated_at DESC").fetchall()]
        credit_purchases = [dict(r) for r in db.execute("SELECT * FROM credit_purchases ORDER BY created_at DESC LIMIT 100").fetchall()]
        credit_balances = [dict(r) for r in db.execute("SELECT * FROM credits WHERE balance > 0 ORDER BY balance DESC").fetchall()]
        affiliates = [dict(r) for r in db.execute("SELECT * FROM affiliates ORDER BY total_earned DESC").fetchall()]
        referrals = [dict(r) for r in db.execute("SELECT * FROM referrals ORDER BY created_at DESC LIMIT 100").fetchall()]
        stats = {
            "total": db.execute("SELECT COUNT(*) FROM payments").fetchone()[0],
            "pending": db.execute("SELECT COUNT(*) FROM payments WHERE status='pending'").fetchone()[0],
            "activated": db.execute("SELECT COUNT(*) FROM payments WHERE status='activated'").fetchone()[0],
            "pro_count": db.execute("SELECT COUNT(*) FROM pro_users").fetchone()[0],
            "credit_sales": db.execute("SELECT COUNT(*) FROM credit_purchases WHERE status='activated'").fetchone()[0],
            "credit_revenue": db.execute("SELECT COALESCE(SUM(amount_usd),0) FROM credit_purchases WHERE status='activated'").fetchone()[0],
            "credit_pending": db.execute("SELECT COUNT(*) FROM credit_purchases WHERE status='pending'").fetchone()[0],
        }
    flash = session.pop('admin_flash', None)
    return render_template_string(ADMIN_HTML, stats=stats, all_payments=all_payments,
        pending_payments=pending_payments, pending_count=len(pending_payments),
        pro_users=pro_users, credit_purchases=credit_purchases, credit_balances=credit_balances,
        affiliates=affiliates, referrals=referrals,
        flash=flash,
        now=datetime.now().strftime("%A, %d %B %Y - %H:%M"))

@app.route('/admin/mark-payout-paid', methods=['POST'])
@admin_required
def mark_payout_paid():
    data = request.get_json(silent=True) or {}
    affiliate_id = data.get('affiliate_id')
    if not affiliate_id:
        return jsonify({"success": False, "error": "Missing affiliate_id"}), 400
    with get_db() as db:
        db.execute("UPDATE affiliates SET pending_payout = 0 WHERE id = ?", (affiliate_id,))
    return jsonify({"success": True})

@app.route('/admin/activate/<int:payment_id>', methods=['POST'])
@admin_required
def admin_activate(payment_id):
    with get_db() as db:
        row = db.execute("SELECT * FROM payments WHERE id=?", (payment_id,)).fetchone()
        if row:
            db.execute("UPDATE payments SET status='activated', activated_at=datetime('now') WHERE id=?", (payment_id,))
            db.commit()
            purchase = activate_credit_purchase(row['tx_ref'])
            if purchase:
                session['admin_flash'] = f"{purchase['ads']} credits activated for {row['email']}"
            else:
                session['admin_flash'] = f"Payment activated for {row['email']} (no matching credit purchase found)"
        else:
            session['admin_flash'] = "Payment not found."
    return redirect('/admin')

@app.route('/admin/reject/<int:payment_id>', methods=['POST'])
@admin_required
def admin_reject(payment_id):
    with get_db() as db:
        db.execute("UPDATE payments SET status='rejected' WHERE id=?", (payment_id,))
        db.commit()
    session['admin_flash'] = f"Payment {payment_id} rejected."
    return redirect('/admin')

@app.route('/admin/activate-manual', methods=['POST'])
@admin_required
def admin_activate_manual():
    email = request.form.get('email','').strip()
    package = request.form.get('package','basic')
    if package not in CREDIT_PACKAGES:
        package = 'basic'
    pkg = CREDIT_PACKAGES[package]
    if email:
        ref = "manual-"+make_ref()
        ref_code = get_permanent_ref_code(email) or ''
        save_payment(email, "manual", f"${pkg['usd']}", ref, "", "activated")
        save_credit_purchase(email, package, pkg['ads'], pkg['usd'], "manual", "manual", ref, "activated", ref_code=ref_code)
        add_credits(email, pkg['ads'])
        if ref_code:
            commission = round(pkg['usd'] * 0.4, 2)
            record_referral(ref_code, email, commission, ref)
        session['admin_flash'] = f"{pkg['ads']} credits manually added for {email}"
    return redirect('/admin')


@app.route('/affiliate', methods=['GET','POST'])
def affiliate():
    msg = error = None
    if request.method == 'POST':
        name = request.form.get('name','').strip()
        email = request.form.get('email','').strip()
        wallet_coin = request.form.get('wallet_coin','USDT').strip()
        wallet_address = request.form.get('wallet_address','').strip()
        if not name or not email or not wallet_address:
            error = 'All fields are required.'
        else:
            with get_db() as db:
                existing = db.execute("SELECT 1 FROM affiliates WHERE email=?", (email,)).fetchone()
                if existing:
                    error = 'This email is already registered.'
                else:
                    ref_code = make_ref_code(name)
                    db.execute("INSERT INTO affiliates (name,email,ref_code,wallet_coin,wallet_address) VALUES (?,?,?,?,?)", (name, email, ref_code, wallet_coin, wallet_address))
                    db.commit()
                    session['affiliate_code'] = ref_code
                    session['affiliate_email'] = email
                    msg = ref_code
    ref_code = session.get('affiliate_code','')
    app_url = os.environ.get('APP_URL','https://copyswift-ai.onrender.com')
    ref_link = f"{app_url}/?ref={ref_code}" if ref_code else ""
    return render_template('affiliate.html', msg=msg, error=error, ref_code=ref_code, ref_link=ref_link)

@app.route('/affiliate/dashboard')
def affiliate_dashboard():
    email = session.get('affiliate_email','')
    if not email:
        return redirect('/affiliate')
    with get_db() as db:
        aff = db.execute("SELECT * FROM affiliates WHERE email=?", (email,)).fetchone()
        if not aff:
            return redirect('/affiliate')
        referrals = [dict(r) for r in db.execute("SELECT * FROM referrals WHERE ref_code=? ORDER BY created_at DESC", (aff['ref_code'],)).fetchall()]
    app_url = os.environ.get('APP_URL','https://copyswift-ai.onrender.com')
    ref_link = f"{app_url}/?ref={aff['ref_code']}"
    return render_template('affiliate_dash.html', aff=dict(aff), referrals=referrals, ref_link=ref_link)

@app.route('/api/generate-image', methods=['POST'])
def api_generate_image():
    email = session.get('user_email', '')
    if not email:
        return jsonify({"error": "Not logged in"}), 401
    data = request.get_json()
    prompt = data.get('prompt', '').strip()
    if not prompt:
        return jsonify({"error": "Prompt is required"}), 400
    with get_db() as db:
        user = db.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
        if not user:
            return jsonify({"error": "User not found"}), 404
        is_admin = email == os.environ.get("ADMIN_EMAIL", "")
        if not is_admin and user['credits'] < 2:
            return jsonify({"error": "Insufficient credits. Image generation costs 2 credits."}), 402
        image_url = generate_image_and_upload(prompt)
        if not image_url:
            return jsonify({"error": "Image generation failed. Please try again."}), 500
        if not is_admin:
            db.execute("UPDATE users SET credits = credits - 2 WHERE email=?", (email,))
            db.commit()
        return jsonify({"image_url": image_url, "credits_used": 2})

@app.route('/api/check-pro')
def api_check_pro():
    email = request.args.get('email','')
    return jsonify({"pro": is_pro_email(email)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
