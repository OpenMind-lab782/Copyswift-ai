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
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=1)
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
DID_API_KEY = os.environ.get("DID_API_KEY", "")
cloudinary.config(
    cloud_name=os.environ.get("CLOUDINARY_CLOUD_NAME", ""),
    api_key=os.environ.get("CLOUDINARY_API_KEY", ""),
    api_secret=os.environ.get("CLOUDINARY_API_SECRET", "")
)

def generate_image_and_upload(prompt):
    """Call Together AI FLUX.1-schnell, upload result to Cloudinary, return URL."""
    try:
        safe_prompt = prompt + " No text, no words, no letters, no writing, no watermarks. English only visual style."
        headers = {
            "Authorization": f"Bearer {TOGETHER_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "black-forest-labs/FLUX.1-schnell",
            "prompt": safe_prompt,
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
        import traceback
        print(f"Image generation error: {e}")
        print(traceback.format_exc())
        return ""


def enhance_uploaded_image(image_bytes, ad_copy_context=""):
    """Upload user image to Cloudinary and apply professional
    ad enhancement transformations. No AI generation — stays true to original."""
    try:
        original_upload = cloudinary.uploader.upload(
            image_bytes,
            folder="copyswift_ai/originals",
            resource_type="image"
        )
        original_url = original_upload.get("secure_url", "")
        # Apply professional enhancement via Cloudinary transformations
        # Stays true to the original image — no AI hallucination
        enhanced_upload = cloudinary.uploader.upload(
            image_bytes,
            folder="copyswift_ai/enhanced",
            resource_type="image",
            transformation=[
                {"effect": "auto_brightness"},
                {"effect": "auto_contrast"},
                {"effect": "vibrance:40"},
                {"effect": "saturation:20"},
                {"effect": "sharpen:80"},
                {"quality": "auto:best"}
            ]
        )
        enhanced_url = enhanced_upload.get("secure_url", "") or original_url
        return {"original_url": original_url, "enhanced_url": enhanced_url}
    except Exception as e:
        import traceback
        print(f"Image enhancement error: {e}")
        print(traceback.format_exc())
        return None




def start_talking_video(script_text, presenter_id='noelle'):
    """Start a D-ID video generation job. Returns talk_id immediately (non-blocking)."""
    try:
        headers = {
            'Authorization': f'Basic {DID_API_KEY}',
            'Content-Type': 'application/json'
        }
        payload = {
            'script': {
                'type': 'text',
                'input': script_text[:500],
                'provider': {'type': 'microsoft', 'voice_id': 'en-US-JennyNeural'}
            },
            'source_url': 'https://create-images-results.d-id.com/api_docs/assets/noelle.jpeg'
        }
        resp = requests.post('https://api.d-id.com/talks', headers=headers, json=payload, timeout=20)
        if resp.status_code >= 400:
            print('D-ID error response body:', resp.text)
        resp.raise_for_status()
        return resp.json().get('id')
    except Exception as e:
        import traceback
        print(f'Video start error: {e}')
        print(traceback.format_exc())
        return None

def check_talking_video(talk_id):
    """Check status of a D-ID video job. Returns dict with status and url if ready."""
    try:
        headers = {
            'Authorization': f'Basic {DID_API_KEY}',
            'Content-Type': 'application/json'
        }
        check = requests.get(f'https://api.d-id.com/talks/{talk_id}', headers=headers, timeout=15)
        check.raise_for_status()
        data = check.json()
        status = data.get('status')
        if status == 'done':
            raw_url = data.get('result_url')
            upload_result = cloudinary.uploader.upload(
                raw_url,
                folder='copyswift_ai/videos',
                resource_type='video'
            )
            return {'status': 'done', 'video_url': upload_result.get('secure_url', '')}
        elif status == 'error':
            return {'status': 'error'}
        else:
            return {'status': 'pending'}
    except Exception as e:
        import traceback
        print(f'Video check error: {e}')
        print(traceback.format_exc())
        return {'status': 'error'}

FAL_KEY = os.environ.get('FAL_KEY', '')

def start_image_to_video(image_url, prompt='Gentle slow zoom in, product stays still and clearly visible, soft studio lighting, professional advertising style', aspect_ratio='1:1'):
    """Start a fal.ai image-to-video job. Returns request_id immediately (non-blocking)."""
    try:
        headers = {
            'Authorization': f'Key {FAL_KEY}',
            'Content-Type': 'application/json'
        }
        if aspect_ratio not in ('16:9', '9:16', '1:1'):
            aspect_ratio = '1:1'
        payload = {
            'image_url': image_url,
            'prompt': prompt[:500],
            'aspect_ratio': aspect_ratio
        }
        resp = requests.post('https://queue.fal.run/fal-ai/wan-i2v', headers=headers, json=payload, timeout=20)
        if resp.status_code >= 400:
            print('fal.ai error response body:', resp.text)
        resp.raise_for_status()
        data = resp.json()
        return {'request_id': data.get('request_id'), 'status_url': data.get('status_url'), 'response_url': data.get('response_url')}
    except Exception as e:
        import traceback
        print(f'Image-to-video start error: {e}')
        print(traceback.format_exc())
        return None

def check_image_to_video(status_url, response_url):
    """Check status of a fal.ai image-to-video job. Returns dict with status and url if ready."""
    try:
        headers = {'Authorization': f'Key {FAL_KEY}'}
        check = requests.get(status_url, headers=headers, timeout=15)
        check.raise_for_status()
        data = check.json()
        status = data.get('status')
        print(f'fal.ai status check response: {data}')
        if status == 'COMPLETED':
            result = requests.get(response_url, headers=headers, timeout=15)
            if result.status_code >= 400:
                print(f'fal.ai result fetch error body: {result.text}')
                return {'status': 'error', 'message': 'Video generation failed. Please try a different image.'}
            result.raise_for_status()
            result_data = result.json()
            raw_url = result_data.get('video', {}).get('url')
            if not raw_url:
                return {'status': 'error', 'message': 'Video generation failed. Please try a different image.'}
            upload_result = cloudinary.uploader.upload(
                raw_url,
                folder='copyswift_ai/image_to_video',
                resource_type='video'
            )
            return {'status': 'done', 'video_url': upload_result.get('secure_url', '')}
        elif status in ('IN_QUEUE', 'IN_PROGRESS'):
            return {'status': 'pending'}
        else:
            print(f'fal.ai unexpected status payload: {data}')
            return {'status': 'error', 'message': 'Video generation failed. Please try again.'}
    except Exception as e:
        import traceback
        print(f'Image-to-video check error: {e}')
        print(traceback.format_exc())
        return {'status': 'error', 'message': 'Video generation failed. Please try again.'}

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
    "tiktok":       {"label": "🎵 TikTok Script",            "prompt": "Write a TikTok video script for {product} targeting {audience}. Include: a 3-second hook line, 3-4 short talking points to say on camera, a call-to-action closing line, a suggested caption, and 5 relevant trending hashtags. Format clearly with labels."},
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
        db.execute("""CREATE TABLE IF NOT EXISTS business_profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            business_name TEXT NOT NULL,
            product TEXT NOT NULL,
            audience TEXT NOT NULL,
            tone TEXT DEFAULT 'Professional',
            is_active INTEGER DEFAULT 0,
            created_at TEXT DEFAULT (datetime('now'))
        )""")
        db.execute("""CREATE TABLE IF NOT EXISTS user_streaks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email TEXT NOT NULL UNIQUE,
            current_streak INTEGER DEFAULT 0,
            longest_streak INTEGER DEFAULT 0,
            last_activity_date TEXT,
            streak_freezes_available INTEGER DEFAULT 1,
            last_milestone_awarded INTEGER DEFAULT 0,
            created_at TEXT DEFAULT (datetime('now'))
        )""")
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

def get_business_profiles(email):
    with get_db() as db:
        rows = db.execute("SELECT * FROM business_profiles WHERE email=? ORDER BY created_at ASC", (email,)).fetchall()
        return [dict(r) for r in rows]

def get_active_business_profile(email):
    with get_db() as db:
        row = db.execute("SELECT * FROM business_profiles WHERE email=? AND is_active=1", (email,)).fetchone()
        return dict(row) if row else None

def create_business_profile(email, business_name, product, audience, tone):
    with get_db() as db:
        existing = db.execute("SELECT COUNT(*) as c FROM business_profiles WHERE email=?", (email,)).fetchone()
        is_first = existing['c'] == 0
        db.execute(
            "INSERT INTO business_profiles (email, business_name, product, audience, tone, is_active) VALUES (?,?,?,?,?,?)",
            (email, business_name, product, audience, tone, 1 if is_first else 0)
        )
        db.commit()
        new_id = db.execute("SELECT last_insert_rowid() as id").fetchone()['id']
        return new_id

def set_active_business_profile(email, profile_id):
    with get_db() as db:
        db.execute("UPDATE business_profiles SET is_active=0 WHERE email=?", (email,))
        db.execute("UPDATE business_profiles SET is_active=1 WHERE id=? AND email=?", (profile_id, email))
        db.commit()

def update_business_profile(email, profile_id, business_name, product, audience, tone):
    with get_db() as db:
        db.execute(
            "UPDATE business_profiles SET business_name=?, product=?, audience=?, tone=? WHERE id=? AND email=?",
            (business_name, product, audience, tone, profile_id, email)
        )
        db.commit()


def update_streak(email):
    from datetime import date, timedelta
    today = date.today()
    milestone_hit = None
    bonus_credits = 0

    with get_db() as db:
        row = db.execute("SELECT * FROM user_streaks WHERE user_email=?", (email,)).fetchone()

        if not row:
            db.execute(
                "INSERT INTO user_streaks (user_email, current_streak, longest_streak, last_activity_date, streak_freezes_available) VALUES (?,1,1,?,1)",
                (email, today.isoformat())
            )
            db.commit()
            return {"current_streak": 1, "longest_streak": 1, "milestone_hit": None, "bonus_credits": 0}

        last_date_str = row["last_activity_date"]
        current_streak = row["current_streak"]
        longest_streak = row["longest_streak"]
        freezes = row["streak_freezes_available"]
        last_milestone = row["last_milestone_awarded"]

        last_date = date.fromisoformat(last_date_str) if last_date_str else None

        if last_date == today:
            return {"current_streak": current_streak, "longest_streak": longest_streak, "milestone_hit": None, "bonus_credits": 0}
        elif last_date == today - timedelta(days=1):
            current_streak += 1
        elif last_date is not None and last_date == today - timedelta(days=2) and freezes > 0:
            freezes -= 1
            current_streak += 1
        else:
            current_streak = 1

        longest_streak = max(longest_streak, current_streak)

        milestones = {7: 10, 30: 50, 100: 180}
        if current_streak in milestones and last_milestone < current_streak:
            milestone_hit = current_streak
            bonus_credits = milestones[current_streak]
            db.execute("UPDATE credits SET balance = balance + ? WHERE email=?", (bonus_credits, email))
            last_milestone = current_streak

        db.execute(
            "UPDATE user_streaks SET current_streak=?, longest_streak=?, last_activity_date=?, streak_freezes_available=?, last_milestone_awarded=? WHERE user_email=?",
            (current_streak, longest_streak, today.isoformat(), freezes, last_milestone, email)
        )
        db.commit()

    return {"current_streak": current_streak, "longest_streak": longest_streak, "milestone_hit": milestone_hit, "bonus_credits": bonus_credits}


def deduct_credit(email):
    with get_db() as db:
        row = db.execute("SELECT balance FROM credits WHERE email=?", (email,)).fetchone()
        if not row or row["balance"] <= 0:
            return False
        db.execute("UPDATE credits SET balance = balance - 1 WHERE email=?", (email,))
        db.commit()
    update_streak(email)
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
  <a href="/tools/ad-copy" style="display:inline-block;margin-top:14px;font-size:13px;font-weight:600;color:var(--accent);text-decoration:none;border:1px solid rgba(0,212,255,.3);padding:8px 16px;border-radius:100px;background:rgba(0,212,255,.06)">🆓 Try the free Ad Copy Tool →</a>
</div>
<div class="usage-bar">
  <span class="usage-label">{% if credits_balance > 0 %}✅ Credits available{% else %}No credits remaining{% endif %}</span>
  <div class="usage-dots">
    <span style="font-family:'Space Grotesk',sans-serif;font-size:18px;font-weight:700;color:var(--accent)">{{ credits_balance }}</span>
    <span style="color:var(--muted);font-size:12px;margin-left:4px">ad{{ 's' if credits_balance != 1 else '' }} left</span>
  </div>
  <a href="#upgrade" class="upgrade-link">Buy Credits →</a>
</div>
{% if streak_current and streak_current > 0 %}
<div class="usage-bar" style="background:linear-gradient(135deg,rgba(255,107,53,0.15),rgba(247,147,30,0.1));border:1px solid rgba(255,107,53,0.3);margin-top:10px">
  <span class="usage-label">🔥 {{ streak_current }}-day streak</span>
  <div class="usage-dots">
    <span style="color:var(--muted);font-size:12px">Best: {{ streak_longest }} days</span>
  </div>
</div>
{% endif %}
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

    <div id="bizProfileSection" style="margin-bottom:16px">
      <label>Business Profile</label>
      <select id="bizProfileSelect" onchange="onProfileChange()" style="width:100%;padding:12px 15px;background:var(--surface2);border:1px solid var(--border);border-radius:10px;color:var(--text);font-size:15px;margin-bottom:8px">
        <option value="">+ Create New Business Profile</option>
      </select>
      <div id="newProfileForm" style="display:none;background:#1a1a2e;border:1px solid #00d4ff33;border-radius:12px;padding:16px;margin-bottom:8px">
        <label style="font-size:13px">Business Name</label>
        <input type="text" id="bizName" placeholder="e.g. Skin Glow Cosmetics" style="width:100%;padding:10px;background:#0d0d1a;border:1px solid #333;border-radius:8px;color:#fff;font-size:14px;margin-bottom:10px;box-sizing:border-box">
        <label style="font-size:13px">Tone / Language Style</label>
        <select id="bizTone" style="width:100%;padding:10px;background:#0d0d1a;border:1px solid #333;border-radius:8px;color:#fff;font-size:14px;margin-bottom:10px">
          <option>Professional</option>
          <option>Casual</option>
          <option>Funny/Playful</option>
          <option>Nigerian Pidgin English</option>
          <option>Yoruba (Beta)</option>
          <option>Igbo (Beta)</option>
          <option>Hausa</option>
          <option>Urhobo (Beta)</option>
          <option>Isoko (Beta)</option>
          <option>Ijaw (Beta)</option>
          <option>Setswana</option>
          <option>Zulu</option>
        </select>
        <button type="button" onclick="saveBizProfile()" style="width:100%;padding:12px;background:linear-gradient(135deg,#7c3aed,#00d4ff);color:#fff;font-weight:700;border:none;border-radius:8px;cursor:pointer">💾 Save Business Profile</button>
      </div>
    </div>

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
    <button type="button" onclick="generateBundle()" id="bundleBtn" style="width:100%;margin-top:10px;padding:15px;background:linear-gradient(135deg,#ff6b6b,#feca57);color:#fff;font-family:'Space Grotesk',sans-serif;font-size:16px;font-weight:700;border:none;border-radius:12px;cursor:pointer">🎯 Generate Full Campaign (3 credits)</button>
    <div id="bundleStatus" style="text-align:center;color:#888;font-size:13px;margin-top:10px;display:none">⏳ Generating your full campaign, please wait...</div>
    <div id="bundleError" style="color:#ff4444;font-size:13px;margin-top:10px;display:none"></div>
  </form>
</div>
<div id="bundleResults" style="display:none;max-width:540px;margin:0 auto 20px">
  <div class="result-card" style="margin-bottom:12px">
    <div class="result-header">
      <span class="result-label">📣 Facebook / Instagram Ad</span>
      <button class="copy-btn" onclick="copyBundleItem('ad')">📋 Copy</button>
    </div>
    <div class="result-text" id="bundleAdText"></div>
  </div>
  <div class="result-card" style="margin-bottom:12px">
    <div class="result-header">
      <span class="result-label">💬 WhatsApp Sales Message</span>
      <button class="copy-btn" onclick="copyBundleItem('whatsapp')">📋 Copy</button>
    </div>
    <div class="result-text" id="bundleWhatsappText"></div>
  </div>
  <div class="result-card">
    <div class="result-header">
      <span class="result-label">📧 Email Campaign</span>
      <button class="copy-btn" onclick="copyBundleItem('email')">📋 Copy</button>
    </div>
    <div class="result-text" id="bundleEmailText"></div>
  </div>
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
  <div style="font-size:15px;font-weight:700;color:#00d4ff;margin-bottom:8px">🎨 Generate Ad Image (5 credits)</div>
  <div style="font-size:12px;color:#888;margin-bottom:12px">Powered by FLUX.1 AI — describe your ideal ad image</div>
  <textarea id="imgPrompt" placeholder="Describe a VISUAL SCENE only e.g. A professional shop with products on display, bright lighting, vibrant colors. DO NOT paste your ad copy here." style="width:100%;padding:12px;background:#0d0d1a;border:1px solid #333;border-radius:10px;color:#fff;font-size:13px;resize:vertical;min-height:80px;box-sizing:border-box"></textarea>
  <button onclick="generateImage()" id="imgBtn" style="width:100%;margin-top:10px;padding:13px;background:linear-gradient(135deg,#7c3aed,#00d4ff);color:#fff;font-weight:700;font-size:15px;border:none;border-radius:10px;cursor:pointer">🖼️ Generate Image</button>
  <div id="imgStatus" style="text-align:center;color:#888;font-size:13px;margin-top:10px;display:none">⏳ Generating image, please wait 15-30 seconds...</div>
  <div id="imgResult" style="margin-top:15px;display:none">
    <img id="generatedImg" src="" style="width:100%;border-radius:12px;border:1px solid #00d4ff44" />
    <a id="imgDownload" href="" download="copyswift-ad.png" target="_blank" style="display:block;text-align:center;margin-top:10px;color:#00d4ff;font-size:13px">⬇️ Download Image</a>
  </div>
  <div id="imgError" style="color:#ff4444;font-size:13px;margin-top:10px;display:none"></div>
</div>

<div class="image-gen-card" style="background:#1a1a2e;border:1px solid #a855f733;border-radius:16px;padding:20px;margin:20px 0">
  <div style="font-size:15px;font-weight:700;color:#a855f7;margin-bottom:8px">&#128228; Upload &amp; Enhance Your Image (6 credits)</div>
  <div style="font-size:12px;color:#888;margin-bottom:14px">Upload your product photo - AI generates a professional ad version</div>
  <div onclick="document.getElementById('uploadInput').click()" style="border:2px dashed #a855f744;border-radius:12px;padding:24px;text-align:center;cursor:pointer;background:#0d0d1a">
    <div style="font-size:32px;margin-bottom:8px">&#128247;</div>
    <div style="color:#aaa;font-size:13px">Tap to choose your product image</div>
    <div style="color:#666;font-size:11px;margin-top:4px">PNG, JPG, WEBP supported</div>
  </div>
  <input type="file" id="uploadInput" accept="image/*" style="display:none" onchange="previewUpload(this)">
  <div id="uploadPreview" style="display:none;margin-top:14px">
    <img id="previewImg" src="" style="width:100%;border-radius:10px;border:1px solid #a855f744;max-height:200px;object-fit:cover"/>
    <div id="uploadFileName" style="color:#888;font-size:12px;margin-top:6px;text-align:center"></div>
  </div>
  <textarea id="enhanceContext" placeholder="Optional: paste your ad copy here so AI can tailor the image" style="width:100%;margin-top:12px;padding:12px;background:#0d0d1a;border:1px solid #333;border-radius:10px;color:#fff;font-size:13px;resize:vertical;min-height:70px;box-sizing:border-box"></textarea>
  <button onclick="enhanceImage()" id="enhanceBtn" style="width:100%;margin-top:10px;padding:13px;background:linear-gradient(135deg,#a855f7,#7c3aed);color:#fff;font-weight:700;font-size:15px;border:none;border-radius:10px;cursor:pointer">&#10024; Enhance My Image (6 credits)</button>
  <div id="enhanceStatus" style="text-align:center;color:#888;font-size:13px;margin-top:10px;display:none">&#9203; Enhancing your image, please wait 20-40 seconds...</div>
  <div id="enhanceResult" style="margin-top:15px;display:none">
    <div style="font-size:13px;font-weight:700;color:#a855f7;margin-bottom:8px">&#9989; Your Enhanced Ad Image:</div>
    <img id="enhancedImg" src="" style="width:100%;border-radius:12px;border:1px solid #a855f744"/>
    <a id="enhancedDownload" href="" download="copyswift-enhanced.png" target="_blank" style="display:block;text-align:center;margin-top:10px;color:#a855f7;font-size:13px">&#11015; Download Enhanced Image</a>
    <div style="margin-top:12px;font-size:12px;color:#666;text-align:center">Original saved too - <a id="originalLink" href="" target="_blank" style="color:#666">view original</a></div>
  </div>
  <div id="enhanceError" style="color:#ff4444;font-size:13px;margin-top:10px;display:none"></div>
</div>
<div class="image-gen-card" style="background:#1a1a2e;border:1px solid #ff6b3533;border-radius:16px;padding:20px;margin:20px 0">
  <div style="font-size:15px;font-weight:700;color:#ff6b35;margin-bottom:8px">Turn Your Ad Into a Talking Video (15 credits)</div>
  <div style="font-size:12px;color:#888;margin-bottom:14px">AI presenter reads your ad copy out loud</div>
  <textarea id="videoScript" placeholder="Paste or type the script you want the AI presenter to say (max 500 characters)" style="width:100%;padding:12px;background:#0d0d1a;border:1px solid #333;border-radius:10px;color:#fff;font-size:13px;resize:vertical;min-height:90px;box-sizing:border-box" maxlength="500"></textarea>
  <button onclick="generateVideo()" id="videoBtn" style="width:100%;margin-top:10px;padding:13px;background:linear-gradient(135deg,#ff6b35,#f7931e);color:#fff;font-weight:700;font-size:15px;border:none;border-radius:10px;cursor:pointer">Generate Talking Video (15 credits)</button>
  <div id="videoStatus" style="text-align:center;color:#888;font-size:13px;margin-top:10px;display:none">Rendering your video, please wait 30-90 seconds...</div>
  <div id="videoResult" style="margin-top:15px;display:none">
    <video id="generatedVideo" controls style="width:100%;border-radius:12px;border:1px solid #ff6b3544"></video>
    <a id="videoDownload" href="" download="copyswift-video.mp4" target="_blank" style="display:block;text-align:center;margin-top:10px;color:#ff6b35;font-size:13px">Download Video</a>
  </div>
  <div id="videoError" style="color:#ff4444;font-size:13px;margin-top:10px;display:none"></div>
</div>
<script>
async function generateVideo(){
  const script=document.getElementById('videoScript').value.trim();
  if(!script){alert('Please enter a script for the video first.');return;}
  const btn=document.getElementById('videoBtn');
  const status=document.getElementById('videoStatus');
  const result=document.getElementById('videoResult');
  const errDiv=document.getElementById('videoError');
  btn.disabled=true;btn.textContent='Starting...';
  status.style.display='block';result.style.display='none';errDiv.style.display='none';
  status.textContent='Starting video generation...';
  try{
    const resp=await fetch('/api/generate-video',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({script:script,email:document.querySelector('input[name=email]')?.value||''})});
    const data=await resp.json();
    if(!data.talk_id){
      errDiv.textContent=data.error||'Video generation failed to start.';
      errDiv.style.display='block';status.style.display='none';
      btn.disabled=false;btn.textContent='Generate Talking Video (15 credits)';
      return;
    }
    btn.textContent='Rendering...';
    status.textContent='Rendering your video, please wait 30-90 seconds...';
    let attempts=0;
    const poll=setInterval(async ()=>{
      attempts++;
      if(attempts>30){
        clearInterval(poll);
        errDiv.textContent='Video is taking longer than expected. Please try again.';
        errDiv.style.display='block';status.style.display='none';
        btn.disabled=false;btn.textContent='Generate Talking Video (15 credits)';
        return;
      }
      try{
        const checkResp=await fetch('/api/check-video/'+data.talk_id);
        const checkData=await checkResp.json();
        if(checkData.status==='done'){
          clearInterval(poll);
          document.getElementById('generatedVideo').src=checkData.video_url;
          document.getElementById('videoDownload').href=checkData.video_url;
          result.style.display='block';status.style.display='none';
          btn.disabled=false;btn.textContent='Generate Talking Video (15 credits)';
        }else if(checkData.status==='error'){
          clearInterval(poll);
          errDiv.textContent='Video generation failed. Please try again.';
          errDiv.style.display='block';status.style.display='none';
          btn.disabled=false;btn.textContent='Generate Talking Video (15 credits)';
        }
      }catch(e){
        clearInterval(poll);
        errDiv.textContent='Error checking video status: '+e.message;
        errDiv.style.display='block';status.style.display='none';
        btn.disabled=false;btn.textContent='Generate Talking Video (15 credits)';
      }
    },4000);
  }catch(e){
    errDiv.textContent='Error: '+e.message;
    errDiv.style.display='block';status.style.display='none';
    btn.disabled=false;btn.textContent='Generate Talking Video (15 credits)';
  }
}
</script>
<script>
function previewUpload(input){
  if(input.files&&input.files[0]){
    const reader=new FileReader();
    reader.onload=function(e){
      document.getElementById('previewImg').src=e.target.result;
      document.getElementById('uploadFileName').textContent=input.files[0].name;
      document.getElementById('uploadPreview').style.display='block';
    };
    reader.readAsDataURL(input.files[0]);
  }
}
async function enhanceImage(){
  const fileInput=document.getElementById('uploadInput');
  if(!fileInput.files||!fileInput.files[0]){alert('Please select an image first.');return;}
  const btn=document.getElementById('enhanceBtn');
  const status=document.getElementById('enhanceStatus');
  const result=document.getElementById('enhanceResult');
  const errDiv=document.getElementById('enhanceError');
  btn.disabled=true;btn.textContent='Enhancing...';
  status.style.display='block';result.style.display='none';errDiv.style.display='none';
  try{
    const formData=new FormData();
    formData.append('image',fileInput.files[0]);
    formData.append('ad_copy',document.getElementById('enhanceContext').value||'');
    formData.append('email',document.querySelector('input[name=email]')?.value||'');
    const resp=await fetch('/api/enhance-image',{method:'POST',body:formData});
    const data=await resp.json();
    if(data.enhanced_url){
      document.getElementById('enhancedImg').src=data.enhanced_url;
      document.getElementById('enhancedDownload').href=data.enhanced_url;
      document.getElementById('originalLink').href=data.original_url||'#';
      result.style.display='block';status.style.display='none';
    }else{
      errDiv.textContent=data.error||'Enhancement failed.';
      errDiv.style.display='block';status.style.display='none';
    }
  }catch(e){
    errDiv.textContent='Error: '+e.message;
    errDiv.style.display='block';status.style.display='none';
  }finally{
    btn.disabled=false;btn.textContent='Enhance My Image (6 credits)';
    status.style.display='none';
  }
}
</script>

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
let bundleData = {};
async function generateBundle(){
  const email = document.querySelector('input[name=email]').value.trim();
  const product = document.querySelector('input[name=product]').value.trim();
  const audience = document.querySelector('input[name=audience]').value.trim();
  if(!email){ alert('Please enter your email first.'); return; }
  if(!product){ alert('Please enter what you are selling first.'); return; }
  const btn = document.getElementById('bundleBtn');
  const status = document.getElementById('bundleStatus');
  const errDiv = document.getElementById('bundleError');
  const resultsDiv = document.getElementById('bundleResults');
  btn.disabled = true;
  btn.textContent = '⏳ Generating...';
  status.style.display = 'block';
  errDiv.style.display = 'none';
  resultsDiv.style.display = 'none';
  try{
    const resp = await fetch('/api/generate-bundle', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({email, product, audience})});
    const data = await resp.json();
    if(data.success){
      bundleData = data.results;
      document.getElementById('bundleAdText').textContent = data.results.ad;
      document.getElementById('bundleWhatsappText').textContent = data.results.whatsapp;
      document.getElementById('bundleEmailText').textContent = data.results.email;
      resultsDiv.style.display = 'block';
      status.style.display = 'none';
    }else{
      errDiv.textContent = data.error || 'Campaign generation failed.';
      errDiv.style.display = 'block';
      status.style.display = 'none';
    }
  }catch(e){
    errDiv.textContent = 'Network error. Please try again.';
    errDiv.style.display = 'block';
    status.style.display = 'none';
  }
  btn.disabled = false;
  btn.textContent = '🎯 Generate Full Campaign (3 credits)';
}
function copyBundleItem(key){
  const text = bundleData[key] || '';
  navigator.clipboard.writeText(text).then(()=>{
    alert('Copied to clipboard!');
  });
}

let bizProfiles = [];
async function loadBizProfiles(){
  const email = document.querySelector('input[name=email]').value.trim();
  if(!email) return;
  try{
    const resp = await fetch('/api/business-profiles?email=' + encodeURIComponent(email));
    const data = await resp.json();
    bizProfiles = data.profiles || [];
    const sel = document.getElementById('bizProfileSelect');
    sel.innerHTML = '<option value="">+ Create New Business Profile</option>';
    let activeId = null;
    bizProfiles.forEach(p=>{
      const opt = document.createElement('option');
      opt.value = p.id;
      opt.textContent = p.business_name;
      if(p.is_active){ opt.selected = true; activeId = p.id; }
      sel.appendChild(opt);
    });
    if(activeId){
      const active = bizProfiles.find(p=>p.id===activeId);
      applyProfileToForm(active);
      document.getElementById('newProfileForm').style.display = 'none';
    } else if(bizProfiles.length===0){
      document.getElementById('newProfileForm').style.display = 'block';
    }
  }catch(e){ console.log('Could not load business profiles', e); }
}
function applyProfileToForm(p){
  if(!p) return;
  document.querySelector('input[name=product]').value = p.product || '';
  document.querySelector('input[name=audience]').value = p.audience || '';
}
async function onProfileChange(){
  const sel = document.getElementById('bizProfileSelect');
  const val = sel.value;
  const newForm = document.getElementById('newProfileForm');
  if(!val){
    newForm.style.display = 'block';
    return;
  }
  newForm.style.display = 'none';
  const email = document.querySelector('input[name=email]').value.trim();
  await fetch('/api/business-profiles/activate', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({email: email, profile_id: parseInt(val)})});
  const p = bizProfiles.find(x=>x.id===parseInt(val));
  applyProfileToForm(p);
}
async function saveBizProfile(){
  const email = document.querySelector('input[name=email]').value.trim();
  const bizName = document.getElementById('bizName').value.trim();
  const product = document.querySelector('input[name=product]').value.trim();
  const audience = document.querySelector('input[name=audience]').value.trim();
  const tone = document.getElementById('bizTone').value;
  if(!email){ alert('Please enter your email first.'); return; }
  if(!bizName || !product){ alert('Please enter a business name and what you are selling.'); return; }
  const resp = await fetch('/api/business-profiles', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({email, business_name: bizName, product, audience, tone})});
  const data = await resp.json();
  if(data.success){
    document.getElementById('bizName').value='';
    await loadBizProfiles();
  }else{
    alert(data.error || 'Could not save business profile.');
  }
}
document.addEventListener('DOMContentLoaded', function(){
  const emailInput = document.querySelector('input[name=email]');
  if(emailInput){
    if(emailInput.value.trim()) loadBizProfiles();
    emailInput.addEventListener('blur', loadBizProfiles);
  }
});

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
    const resp=await fetch('/api/generate-image',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({prompt:prompt,email:document.querySelector('input[name=email]')?.value||''})});
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
    errDiv.textContent='Error: '+e.message+' | '+e.toString();
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
    <div class="section-title">🎁 Gift Bonus Credits</div>
    <form method="POST" action="/admin/gift-credits" style="background:#111;padding:16px;border-radius:10px;margin-bottom:24px;display:flex;gap:10px;flex-wrap:wrap;align-items:end">
      <div>
        <label style="display:block;font-size:12px;color:#888;margin-bottom:4px">User Email</label>
        <input type="email" name="email" required placeholder="user@example.com" style="padding:8px;border-radius:6px;border:1px solid #333;background:#000;color:#fff">
      </div>
      <div>
        <label style="display:block;font-size:12px;color:#888;margin-bottom:4px">Credits Amount</label>
        <input type="number" name="amount" required min="1" placeholder="50" style="padding:8px;border-radius:6px;border:1px solid #333;background:#000;color:#fff;width:100px">
      </div>
      <div>
        <label style="display:block;font-size:12px;color:#888;margin-bottom:4px">Reason (optional)</label>
        <input type="text" name="reason" placeholder="Loyalty bonus" style="padding:8px;border-radius:6px;border:1px solid #333;background:#000;color:#fff">
      </div>
      <button type="submit" style="padding:9px 20px;background:linear-gradient(135deg,#00d4ff,#7c3aed);color:#fff;border:none;border-radius:6px;font-weight:700;cursor:pointer">Gift Credits</button>
    </form>
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
    streak_current = 0
    streak_longest = 0
    if user_email:
        with get_db() as _db:
            _srow = _db.execute("SELECT current_streak, longest_streak FROM user_streaks WHERE user_email=?", (user_email,)).fetchone()
            if _srow:
                streak_current = _srow["current_streak"]
                streak_longest = _srow["longest_streak"]
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
            base_prompt = COPY_TYPES[selected_type]['prompt'].format(product=product, audience=audience)
            active_profile = get_active_business_profile(user_email) if user_email else None
            tone = active_profile['tone'] if active_profile else 'Professional'
            tone = tone.replace(' (Beta)', '').strip()
            if tone and tone != 'Professional':
                prompt = f"{base_prompt}\n\nIMPORTANT: Write this in a {tone} tone/style. If {tone} refers to a language (e.g. Yoruba, Igbo, Hausa, Zulu, Setswana), write the entire copy in that language. If it refers to a style (e.g. Casual, Funny/Playful, Nigerian Pidgin English), write in English using that style throughout."
            else:
                prompt = base_prompt
            try:
                cc = client.chat.completions.create(messages=[{"role":"user","content":prompt + "\n\nIMPORTANT: Output plain text only. Do not use Markdown formatting such as **, ##, or bullet dashes. Write it exactly as it should appear to the end reader."}], model="openai/gpt-oss-20b", reasoning_effort="low")
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
        crypto_wallets=CRYPTO_WALLETS, promo_error=None,
        streak_current=streak_current, streak_longest=streak_longest)

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
        promo_error="Invalid promo code, or please enter your email and generate at least once first.",
        streak_current=0, streak_longest=0)

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


@app.route('/admin/gift-credits', methods=['POST'])
@admin_required
def admin_gift_credits():
    email = request.form.get('email','').strip()
    amount = request.form.get('amount','').strip()
    reason = request.form.get('reason','Loyalty bonus').strip()
    if email and amount:
        try:
            amount = int(amount)
            if amount > 0:
                add_credits(email, amount)
                session['admin_flash'] = f"Gifted {amount} bonus credits to {email} ({reason})"
            else:
                session['admin_flash'] = "Amount must be a positive number"
        except ValueError:
            session['admin_flash'] = "Invalid amount entered"
    else:
        session['admin_flash'] = "Email and amount are required"
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

@app.route('/api/generate-bundle', methods=['POST'])
def api_generate_bundle():
    data = request.get_json() or {}
    email = session.get('user_email', '') or data.get('email', '')
    if not email:
        return jsonify({"error": "Not logged in"}), 401
    product = data.get('product', '').strip()
    audience = data.get('audience', '').strip() or 'customers'
    if not product:
        return jsonify({"error": "Product is required"}), 400

    is_admin = email == os.environ.get('ADMIN_EMAIL', '')
    with get_db() as db:
        balance = get_credit_balance(email)
        if not is_admin and balance < 3:
            return jsonify({"error": "Insufficient credits. Campaign bundle costs 3 credits."}), 402

        active_profile = get_active_business_profile(email)
        tone = active_profile['tone'] if active_profile else 'Professional'
        tone = tone.replace(' (Beta)', '').strip()

        bundle_keys = ['ad', 'whatsapp', 'email']
        results = {}
        try:
            for key in bundle_keys:
                base_prompt = COPY_TYPES[key]['prompt'].format(product=product, audience=audience)
                if tone and tone != 'Professional':
                    prompt = f"{base_prompt}\n\nIMPORTANT: Write this in a {tone} tone/style. If {tone} refers to a language, write the entire copy in that language. If it refers to a style, write in English using that style throughout."
                else:
                    prompt = base_prompt
                cc = client.chat.completions.create(messages=[{"role":"user","content":prompt + "\n\nIMPORTANT: Output plain text only. Do not use Markdown formatting such as **, ##, or bullet dashes. Write it exactly as it should appear to the end reader."}], model="openai/gpt-oss-20b", reasoning_effort="low")
                results[key] = cc.choices[0].message.content
        except Exception as e:
            return jsonify({"error": str(e)}), 500

        if not is_admin:
            db.execute('UPDATE credits SET balance = balance - 3 WHERE email=?', (email,))
            db.commit()

        return jsonify({
            "success": True,
            "credits_used": 3,
            "results": {
                "ad": results.get('ad', ''),
                "whatsapp": results.get('whatsapp', ''),
                "email": results.get('email', '')
            }
        })

@app.route('/api/generate-image', methods=['POST'])
def api_generate_image():
    data = request.get_json() or {}
    email = session.get('user_email', '') or data.get('email', '')
    if not email:
        return jsonify({"error": "Not logged in"}), 401
    prompt = data.get('prompt', '').strip()
    if not prompt:
        return jsonify({"error": "Prompt is required"}), 400
    is_admin = email == os.environ.get("ADMIN_EMAIL", "")
    with get_db() as db:
        balance = get_credit_balance(email)
        if not is_admin and balance < 5:
            return jsonify({"error": "Insufficient credits. Image generation costs 5 credits."}), 402
        image_url = generate_image_and_upload(prompt)
        if not image_url:
            return jsonify({"error": image_url or "Image generation failed. Please try again."}), 500
        if not is_admin:
            db.execute("UPDATE credits SET balance = balance - 5 WHERE email=?", (email,))
            db.commit()
        return jsonify({"image_url": image_url, "credits_used": 5})


@app.route('/api/enhance-image', methods=['POST'])
def api_enhance_image():
    email = session.get('user_email', '') or request.form.get('email', '')
    if not email:
        return jsonify({'error': 'Not logged in'}), 401
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    allowed = {'png','jpg','jpeg','webp','gif'}
    ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''
    if ext not in allowed:
        return jsonify({'error': 'Please upload PNG, JPG, WEBP or GIF'}), 400
    ad_copy_context = request.form.get('ad_copy', '').strip()
    is_admin = email == os.environ.get('ADMIN_EMAIL', '')
    with get_db() as db:
        balance = get_credit_balance(email)
        if not is_admin and balance < 6:
            return jsonify({'error': 'Insufficient credits. Costs 6 credits.'}), 402
        image_bytes = file.read()
        result = enhance_uploaded_image(image_bytes, ad_copy_context)
        if not result:
            return jsonify({'error': 'Enhancement failed. Please try again.'}), 500
        if not is_admin:
            db.execute('UPDATE credits SET balance = balance - 6 WHERE email=?', (email,))
            db.commit()
        return jsonify({'original_url': result['original_url'], 'enhanced_url': result['enhanced_url'], 'credits_used': 6})


@app.route('/api/generate-video', methods=['POST'])
def api_generate_video():
    data = request.get_json() or {}
    email = session.get('user_email', '') or data.get('email', '')
    if not email:
        return jsonify({'error': 'Not logged in'}), 401
    script_text = data.get('script', '').strip()
    if not script_text:
        return jsonify({'error': 'Script text is required'}), 400
    is_admin = email == os.environ.get('ADMIN_EMAIL', '')
    with get_db() as db:
        balance = get_credit_balance(email)
        if not is_admin and balance < 15:
            return jsonify({'error': 'Insufficient credits. Video generation costs 15 credits.'}), 402
        talk_id = start_talking_video(script_text)
        if not talk_id:
            return jsonify({'error': 'Video generation failed to start. Please try again.'}), 500
        if not is_admin:
            db.execute('UPDATE credits SET balance = balance - 15 WHERE email=?', (email,))
            db.commit()
        return jsonify({'talk_id': talk_id})

@app.route('/api/check-video/<talk_id>')
def api_check_video(talk_id):
    result = check_talking_video(talk_id)
    return jsonify(result)

@app.route('/api/generate-image-video', methods=['POST'])
def api_generate_image_video():
    data = request.get_json() or {}
    email = session.get('user_email', '') or data.get('email', '')
    if not email:
        return jsonify({'error': 'Not logged in'}), 401
    image_url = data.get('image_url', '').strip()
    prompt = data.get('prompt', '').strip()
    if not image_url:
        return jsonify({'error': 'An image URL is required'}), 400
    is_admin = email == os.environ.get('ADMIN_EMAIL', '')
    with get_db() as db:
        balance = get_credit_balance(email)
        if not is_admin and balance < 20:
            return jsonify({'error': 'Insufficient credits. Image-to-video costs 20 credits.'}), 402
        job = start_image_to_video(image_url, prompt) if prompt else start_image_to_video(image_url)
        if not job or not job.get('request_id'):
            return jsonify({'error': 'Image-to-video generation failed to start. Please try again.'}), 500
        if not is_admin:
            db.execute('UPDATE credits SET balance = balance - 20 WHERE email=?', (email,))
            db.commit()
        return jsonify({
            'request_id': job['request_id'],
            'status_url': job['status_url'],
            'response_url': job['response_url'],
        })

@app.route('/api/check-image-video', methods=['POST'])
def api_check_image_video():
    data = request.get_json() or {}
    status_url = data.get('status_url', '')
    response_url = data.get('response_url', '')
    if not status_url or not response_url:
        return jsonify({'error': 'Missing status_url or response_url'}), 400
    result = check_image_to_video(status_url, response_url)
    return jsonify(result)

@app.route('/api/streak', methods=['GET'])
def api_get_streak():
    email = session.get('user_email', '') or request.args.get('email', '')
    if not email:
        return jsonify({"error": "Not logged in"}), 401
    with get_db() as db:
        row = db.execute("SELECT * FROM user_streaks WHERE user_email=?", (email,)).fetchone()
    if not row:
        return jsonify({"current_streak": 0, "longest_streak": 0, "streak_freezes_available": 1})
    return jsonify({
        "current_streak": row["current_streak"],
        "longest_streak": row["longest_streak"],
        "streak_freezes_available": row["streak_freezes_available"],
        "last_activity_date": row["last_activity_date"]
    })

@app.route('/api/business-profiles', methods=['GET'])
def api_get_business_profiles():
    email = session.get('user_email', '') or request.args.get('email', '')
    if not email:
        return jsonify({"error": "Not logged in"}), 401
    profiles = get_business_profiles(email)
    return jsonify({"profiles": profiles})

@app.route('/api/business-profiles', methods=['POST'])
def api_create_business_profile():
    data = request.get_json() or {}
    email = session.get('user_email', '') or data.get('email', '')
    if not email:
        return jsonify({"error": "Not logged in"}), 401
    business_name = data.get('business_name', '').strip()
    product = data.get('product', '').strip()
    audience = data.get('audience', '').strip()
    tone = data.get('tone', 'Professional').strip()
    if not business_name or not product:
        return jsonify({"error": "Business name and product are required"}), 400
    new_id = create_business_profile(email, business_name, product, audience, tone)
    set_active_business_profile(email, new_id)
    return jsonify({"success": True, "profile_id": new_id})

@app.route('/api/business-profiles/activate', methods=['POST'])
def api_activate_business_profile():
    data = request.get_json() or {}
    email = session.get('user_email', '') or data.get('email', '')
    if not email:
        return jsonify({"error": "Not logged in"}), 401
    profile_id = data.get('profile_id')
    if not profile_id:
        return jsonify({"error": "profile_id is required"}), 400
    set_active_business_profile(email, profile_id)
    return jsonify({"success": True})

@app.route('/api/business-profiles/update', methods=['POST'])
def api_update_business_profile():
    data = request.get_json() or {}
    email = session.get('user_email', '') or data.get('email', '')
    if not email:
        return jsonify({"error": "Not logged in"}), 401
    profile_id = data.get('profile_id')
    business_name = data.get('business_name', '').strip()
    product = data.get('product', '').strip()
    audience = data.get('audience', '').strip()
    tone = data.get('tone', 'Professional').strip()
    if not profile_id or not business_name or not product:
        return jsonify({"error": "profile_id, business_name and product are required"}), 400
    update_business_profile(email, profile_id, business_name, product, audience, tone)
    return jsonify({"success": True})

@app.route('/api/check-pro')
def api_check_pro():
    email = request.args.get('email','')
    return jsonify({"pro": is_pro_email(email)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
# === APPEND THIS BLOCK TO THE END OF app.py (before any if __name__ == '__main__') ===
# Reuses your existing `client` (Groq) and session-based patterns already in app.py.
# Does NOT touch your credits table — free tool uses its own daily session counter.

from datetime import date as _date

INDUSTRY_VARIANTS = {
    "fashion-retail": {
        "label": "Fashion & Ankara Retail",
        "meta_title": "Free AI Ad Copy Generator for Fashion & Ankara Retail | CopySwift AI",
        "meta_description": "Generate Facebook, WhatsApp & Instagram ad copy for fashion and Ankara retail brands. Free, no signup.",
        "headline": ["Ad copy that", "sells the outfit", "not just the fabric"],
        "offer_placeholder": "e.g. Ankara dresses, made-to-order, delivery across Gaborone",
        "customer_placeholder": "e.g. Women 25-40 shopping for weekend events",
        "hesitation_placeholder": "e.g. Not sure it'll arrive in time",
    },
    "real-estate": {
        "label": "Real Estate",
        "meta_title": "Free AI Ad Copy Generator for Real Estate Agents | CopySwift AI",
        "meta_description": "Write listing ad copy for Facebook and WhatsApp groups that gets DMs, not just likes. Free, no signup.",
        "headline": ["Listings that get", "DMs", "not just likes"],
        "offer_placeholder": "e.g. 2-bedroom flat, Phakalane, move-in ready",
        "customer_placeholder": "e.g. Young professionals relocating to Gaborone",
        "hesitation_placeholder": "e.g. Worried about hidden fees",
    },
    "restaurants": {
        "label": "Restaurants & Food Vendors",
        "meta_title": "Free AI Ad Copy Generator for Restaurants & Food Vendors | CopySwift AI",
        "meta_description": "Generate ad copy for daily specials, delivery menus, and weekend promos. Free, no signup.",
        "headline": ["Ad copy that", "fills tables", "not just feeds"],
        "offer_placeholder": "e.g. Jollof rice combo, delivery within 30 minutes",
        "customer_placeholder": "e.g. Office workers ordering lunch",
        "hesitation_placeholder": "e.g. Unsure delivery will arrive hot",
    },
    "salons-beauty": {
        "label": "Salons & Beauty",
        "meta_title": "Free AI Ad Copy Generator for Salons & Beauty Brands | CopySwift AI",
        "meta_description": "Fill weekend booking slots with ad copy built for last-minute decisions. Free, no signup.",
        "headline": ["Ad copy that", "fills your chair", "this weekend"],
        "offer_placeholder": "e.g. Braids and weave install, walk-ins welcome",
        "customer_placeholder": "e.g. Women booking for a weekend event",
        "hesitation_placeholder": "e.g. Not sure there's a slot open",
    },
    "church-community": {
        "label": "Church & Community Orgs",
        "meta_title": "Free AI Ad Copy Generator for Churches & Community Orgs | CopySwift AI",
        "meta_description": "Write event and fundraiser copy that reads like it's from your community. Free, no signup.",
        "headline": ["Ad copy that", "sounds like", "your community"],
        "offer_placeholder": "e.g. Sunday youth fundraiser, building fund",
        "customer_placeholder": "e.g. Church members and local families",
        "hesitation_placeholder": "e.g. Unsure where the funds go",
    },
    "agencies": {
        "label": "Agencies",
        "meta_title": "Free AI Ad Copy Generator for Agencies | CopySwift AI",
        "meta_description": "Pitch and produce client ad copy in minutes, not a content calendar meeting. Free, no signup.",
        "headline": ["Client-ready copy", "in minutes", "not meetings"],
        "offer_placeholder": "e.g. Client's product launch, three ad variations needed",
        "customer_placeholder": "e.g. Client's target ICP",
        "hesitation_placeholder": "e.g. Budget-conscious client",
    },
    "freelancers": {
        "label": "Freelancers & Consultants",
        "meta_title": "Free AI Ad Copy Generator for Freelancers & Consultants | CopySwift AI",
        "meta_description": "Sound like a full marketing team without hiring one. Free, no signup.",
        "headline": ["Sound like", "a full team", "of one"],
        "offer_placeholder": "e.g. Freelance web design package",
        "customer_placeholder": "e.g. Small business owners without a website",
        "hesitation_placeholder": "e.g. Worried it's too expensive",
    },
    "crypto-web3": {
        "label": "Crypto & Web3",
        "meta_title": "Free AI Ad Copy Generator for Crypto & Web3 | CopySwift AI",
        "meta_description": "Write ad copy for crypto and Web3 products that builds trust fast. Free, no signup.",
        "headline": ["Ad copy that", "builds trust", "fast"],
        "offer_placeholder": "e.g. BWP/USDT swap service, same-day settlement",
        "customer_placeholder": "e.g. First-time crypto users in Botswana",
        "hesitation_placeholder": "e.g. Worried it's a scam",
    },
    "logistics": {
        "label": "Logistics & Delivery",
        "meta_title": "Free AI Ad Copy Generator for Logistics & Delivery | CopySwift AI",
        "meta_description": "Write ad copy that proves speed and reliability. Free, no signup.",
        "headline": ["Ad copy that", "proves you're", "reliable"],
        "offer_placeholder": "e.g. Same-day parcel delivery, Gaborone metro",
        "customer_placeholder": "e.g. Small online sellers needing delivery",
        "hesitation_placeholder": "e.g. Past bad experience with couriers",
    },
}

DAILY_FREE_LIMIT = 3
_DEFAULT_VARIANT = {
    "label": None,
    "meta_title": "Free AI Ad Copy Generator for African Businesses | CopySwift AI",
    "meta_description": "Generate Facebook, WhatsApp & Instagram ad copy for African businesses. Free, no signup.",
    "headline": ["Ad copy that", "sells here", "not just anywhere"],
    "offer_placeholder": "e.g. Ankara dresses, made-to-order, delivery across Gaborone",
    "customer_placeholder": "e.g. Women 25-40 shopping for weekend events",
    "hesitation_placeholder": "e.g. Not sure it'll arrive in time",
}

def _ad_copy_usage_key():
    return f"ad_copy_free_uses:{_date.today().isoformat()}"

def _ad_copy_remaining_uses():
    session.permanent = True
    used = session.get(_ad_copy_usage_key(), 0)
    return max(0, DAILY_FREE_LIMIT - used)

def _ad_copy_increment_uses():
    key = _ad_copy_usage_key()
    session[key] = session.get(key, 0) + 1


@app.route('/tools/ad-copy')
def ad_copy_default():
    return render_template(
        "tools_ad_copy.html",
        industry=None,
        variant=_DEFAULT_VARIANT,
        remaining_uses=_ad_copy_remaining_uses(),
        canonical_path="/tools/ad-copy",
    )


@app.route('/tools/ad-copy/<industry>')
def ad_copy_variant(industry):
    variant = INDUSTRY_VARIANTS.get(industry)
    if variant is None:
        return ad_copy_default()
    return render_template(
        "tools_ad_copy.html",
        industry=industry,
        variant=variant,
        remaining_uses=_ad_copy_remaining_uses(),
        canonical_path=f"/tools/ad-copy/{industry}",
    )


@app.route('/tools/ad-copy/generate', methods=['POST'])
def ad_copy_generate():
    remaining = _ad_copy_remaining_uses()
    if remaining <= 0:
        return jsonify({
            "error": "daily_limit_reached",
            "message": "You've used today's 3 free generations. Sign up free for 5 more across every CopySwift AI tool.",
        }), 429

    data = request.get_json(force=True) or {}
    offer = (data.get("offer") or "").strip()
    customer = (data.get("customer") or "").strip()
    hesitation = (data.get("hesitation") or "").strip()
    platform = data.get("platform", "WhatsApp Status")
    tone = data.get("tone", "Warm & Local")

    if not offer:
        return jsonify({"error": "missing_offer", "message": "Tell us what you're selling first."}), 400

    prompt = (
        f"Write 3 short ad copy variations for {platform}, in a {tone} tone.\n"
        f"What's being sold: {offer}\n"
        f"Target customer: {customer or 'general African small business customers'}\n"
        f"Their main hesitation to address: {hesitation or 'none specified'}\n"
        f"Each variation must be under 60 words, include a hook, the pitch, and a clear call-to-action. "
        f"Separate the 3 variations with '---'. Write in plain text only — no Markdown, no **, no ## headers, no bullet symbols."
    )

    try:
        cc = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="openai/gpt-oss-20b",
            reasoning_effort="low",
        )
        result = cc.choices[0].message.content
        variations = [v.strip() for v in result.split('---') if v.strip()]
    except Exception as e:
        return jsonify({"error": "generation_failed", "message": str(e)}), 500

    _ad_copy_increment_uses()
    return jsonify({
        "variations": variations,
        "remaining_uses": _ad_copy_remaining_uses(),
    })

# === END BLOCK ===
# === APPEND THIS BLOCK TO THE END OF app.py ===
import re as _re
from bs4 import BeautifulSoup as _BeautifulSoup

def _extract_price(soup):
    # Try common price patterns: itemprop, class names, then a regex fallback
    price_tag = soup.find(attrs={"itemprop": "price"})
    if price_tag:
        val = price_tag.get("content") or price_tag.get_text(strip=True)
        if val:
            return val.strip()
    for cls_kw in ["price", "product-price", "current-price"]:
        tag = soup.find(class_=_re.compile(cls_kw, _re.I))
        if tag:
            text = tag.get_text(strip=True)
            if text and len(text) < 30:
                return text
    # Regex fallback: currency symbol followed by digits
    text = soup.get_text(" ", strip=True)
    match = _re.search(r'(P|R|\$|₦|N|BWP|NGN|USD)\s?[\d,]+(\.\d{2})?', text)
    return match.group(0) if match else None


@app.route('/tools/ad-copy/scrape-url', methods=['POST'])
def ad_copy_scrape_url():
    data = request.get_json(force=True) or {}
    url = (data.get("url") or "").strip()

    if not url or not url.startswith(("http://", "https://")):
        return jsonify({"error": "invalid_url", "message": "Please enter a valid product URL starting with http:// or https://"}), 400

    try:
        resp = requests.get(
            url,
            headers={"User-Agent": "Mozilla/5.0 (compatible; CopySwiftAI/1.0)"},
            timeout=8,
        )
        resp.raise_for_status()
    except Exception as e:
        return jsonify({"error": "fetch_failed", "message": f"Couldn't load that page: {str(e)}"}), 400

    soup = _BeautifulSoup(resp.text, "html.parser")

    og_title = soup.find("meta", property="og:title")
    og_desc = soup.find("meta", property="og:description")
    meta_desc = soup.find("meta", attrs={"name": "description"})
    title_tag = soup.find("title")

    title = (og_title.get("content") if og_title else None) or \
             (title_tag.get_text(strip=True) if title_tag else "") or ""
    description = (og_desc.get("content") if og_desc else None) or \
                  (meta_desc.get("content") if meta_desc else "") or ""
    price = _extract_price(soup)

    title = title.strip()[:150]
    description = description.strip()[:300]

    if not title and not description:
        return jsonify({
            "error": "no_content",
            "message": "Couldn't find product details on that page. Try typing your offer manually instead.",
        }), 400

    suggested_offer = title
    if description:
        suggested_offer += f" — {description}"
    if price:
        suggested_offer += f" (Price: {price})"

    return jsonify({
        "title": title,
        "description": description,
        "price": price,
        "suggested_offer": suggested_offer[:400],
    })

# === END BLOCK ===
