from flask import Flask, render_template_string, request, session, redirect, jsonify
from groq import Groq
import os, hashlib, json, requests, time, sqlite3
from datetime import datetime
from functools import wraps

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "copyswift-secret-2024")
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

FREE_LIMIT = 3
DB_PATH = "copyswift.db"
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin123")

PAYSTACK_SECRET = os.environ.get("PAYSTACK_SECRET_KEY", "")
PRO_PRICE_NGN = 5000
CASHAPP_TAG = os.environ.get("CASHAPP_TAG", "$YourCashTag")
CASHAPP_AMOUNT = 5

CRYPTO_WALLETS = {
    "BNB":  {"address": os.environ.get("BNB_WALLET",  "YOUR_BNB_ADDRESS"),  "network": "BEP-20 (BSC)", "amount": "0.008 BNB", "icon": "🟡"},
    "TRX":  {"address": os.environ.get("TRX_WALLET",  "YOUR_TRX_ADDRESS"),  "network": "TRON",         "amount": "15 TRX",    "icon": "🔴"},
    "USDT": {"address": os.environ.get("USDT_WALLET", "YOUR_USDT_ADDRESS"), "network": "TRC-20",       "amount": "5 USDT",    "icon": "🟢"},
    "MATIC":{"address": os.environ.get("MATIC_WALLET","YOUR_MATIC_ADDRESS"),"network": "Polygon",      "amount": "8 MATIC",   "icon": "🟣"},
    "TON":  {"address": os.environ.get("TON_WALLET",  "YOUR_TON_ADDRESS"),  "network": "TON",          "amount": "2 TON",     "icon": "🔵"},
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
  <span class="usage-label">{% if is_pro %}✅ Pro — Unlimited{% else %}Free generations{% endif %}</span>
  <div class="usage-dots">
    {% if is_pro %}{% for i in range(5) %}<div class="dot pro"></div>{% endfor %}
    {% else %}{% for i in range(free_limit) %}<div class="dot {% if i < used %}used{% endif %}"></div>{% endfor %}
    <div class="dot pro"></div><div class="dot pro"></div>{% endif %}
  </div>
  {% if not is_pro %}<a href="#upgrade" class="upgrade-link">Go Pro →</a>
  {% else %}<span style="font-size:12px;color:var(--success);font-weight:600">PRO ✨</span>{% endif %}
</div>
{% if is_pro %}
<div class="success-banner"><span>🎉</span><p><strong>Pro access active!</strong> Unlimited AI copy. Welcome aboard.</p></div>
{% endif %}
{% if limit_reached and not is_pro %}
<div class="paywall" id="upgrade">
  <div class="paywall-header">
    <div style="font-size:36px;margin-bottom:10px">🔒</div>
    <h2>Upgrade to Pro</h2>
    <p>You've used your {{ free_limit }} free generations.<br>Get <strong>unlimited AI copy</strong> for just <strong>$5/month</strong>.</p>
  </div>
  <div class="pay-grid">
    <a href="/pay-paystack" class="pay-method">
      <div class="pay-icon">💳</div><div class="pay-title">Card / Bank</div>
      <div class="pay-sub">Debit card, bank transfer</div>
      <span class="pay-badge badge-green">Paystack · ₦5,000</span>
    </a>
    <a href="{{ cashapp_url }}" target="_blank" class="pay-method" onclick="showCashApp()">
      <div class="pay-icon">💸</div><div class="pay-title">Cash App</div>
      <div class="pay-sub">Send ${{ cashapp_amount }} USD</div>
      <span class="pay-badge badge-green">{{ cashapp_tag }}</span>
    </a>
    <div class="pay-method crypto-method" onclick="openCryptoModal()">
      <div class="pay-icon">🪙</div>
      <div class="pay-title">Crypto — BNB · TRX · USDT · MATIC · TON</div>
      <div class="pay-sub">Low-fee coins · ~$5 equivalent</div>
      <span class="pay-badge badge-gold">No bank needed</span>
    </div>
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
    <h3>🪙 Pay with Crypto</h3>
    <p>Choose a coin, send the exact amount, then submit your TX hash below.</p>
    <div class="coin-tabs">
      {% for coin, info in crypto_wallets.items() %}
      <div class="coin-tab {% if loop.first %}active{% endif %}" onclick="selectCoin('{{ coin }}')">{{ info.icon }} {{ coin }}</div>
      {% endfor %}
    </div>
    {% for coin, info in crypto_wallets.items() %}
    <div class="coin-detail {% if loop.first %}active{% endif %}" id="coin-{{ coin }}">
      <div class="wallet-amount">{{ info.amount }} ≈ $5</div>
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
      <input type="hidden" name="coin" id="selected_coin_input" value="{{ list(crypto_wallets.keys())[0] }}">
      <button type="submit" class="confirm-btn">✅ I've Sent Payment — Activate Pro</button>
    </form>
  </div>
</div>
{% else %}
<div class="card">
  {% if error %}<div class="error">⚠️ {{ error }}</div>{% endif %}
  <form method="POST" id="copyForm">
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
    <button type="submit" class="generate-btn" id="genBtn">⚡ Generate Copy{% if not is_pro %} ({{ free_limit - used }} left){% endif %}</button>
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
{% endif %}
{% endif %}
<div class="features">
  <div class="feature"><div class="feature-icon">📣</div><div class="feature-title">6 Copy Types</div><div class="feature-desc">Ads, email, WhatsApp & more</div></div>
  <div class="feature"><div class="feature-icon">⚡</div><div class="feature-title">Instant AI</div><div class="feature-desc">Results in 5 seconds</div></div>
  <div class="feature"><div class="feature-icon">🌍</div><div class="feature-title">Any Market</div><div class="feature-desc">African & global use</div></div>
</div>
<script>
function selectType(key,el){document.querySelectorAll('.copy-type-btn').forEach(b=>b.classList.remove('selected'));el.classList.add('selected');document.getElementById('copy_type_input').value=key}
function copyResult(){const t=document.getElementById('resultText').innerText;navigator.clipboard.writeText(t).then(()=>{const b=document.querySelector('.copy-btn');b.textContent='✅ Copied!';setTimeout(()=>b.textContent='📋 Copy',2000)})}
document.getElementById('copyForm')?.addEventListener('submit',function(){const b=document.getElementById('genBtn');b.disabled=true;b.textContent='⚡ Generating...'})
function openCryptoModal(){document.getElementById('cryptoModal').classList.add('open')}
function closeCryptoModal(){document.getElementById('cryptoModal').classList.remove('open')}
function selectCoin(coin){document.querySelectorAll('.coin-tab').forEach(t=>t.classList.remove('active'));document.querySelectorAll('.coin-detail').forEach(d=>d.classList.remove('active'));event.target.classList.add('active');document.getElementById('coin-'+coin).classList.add('active');document.getElementById('selected_coin_input').value=coin}
function copyAddr(coin){const addr=document.getElementById('addr-'+coin).innerText;navigator.clipboard.writeText(addr).then(()=>{const b=event.target;b.textContent='✅ Copied!';setTimeout(()=>b.textContent='📋 Copy '+coin+' Address',2000)})}
function showCashApp(){setTimeout(()=>alert('Send $5 to {{ cashapp_tag }} on Cash App.\\n\\nAfter sending, email your screenshot to:\\ncopyswift.support@gmail.com\\n\\nSubject: CopySwift Pro - Cash App\\nInclude your email. Pro activates within the hour.'),300)}
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
    <span class="nav-section">Users</span>
    <a class="nav-item" href="/admin#pro-users">✨ Pro Users</a>
    <a class="nav-item" href="/admin#manual">➕ Activate Manually</a>
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
    <a name="manual"></a>
    <div class="manual-card">
      <h3>➕ Activate Pro Manually</h3>
      <p style="font-size:13px;color:var(--muted);margin-bottom:14px">Enter customer email to grant Pro access instantly.</p>
      <form method="POST" action="/admin/activate-manual">
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
  </div>
</div>
{% if flash %}<div class="toast show" id="toast">{{ flash }}</div>
<script>setTimeout(()=>document.getElementById('toast').classList.remove('show'),3500)</script>{% endif %}
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
  <h2>Pay with Card / Bank</h2>
  <p>₦5,000/month · ~$5 USD. Secure payment via Paystack.</p>
  {% if error %}<div class="err">{{ error }}</div>{% endif %}
  <form method="POST">
    <label>Your Email Address</label>
    <input type="email" name="email" placeholder="you@email.com" required value="{{ email or '' }}">
    <button type="submit" class="pay-btn">🔒 Pay ₦5,000 Securely</button>
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
  <p>Pro access activates within <strong>30–60 minutes</strong>.</p>
  <a href="/" class="home-btn">Back to CopySwift</a>
</div></body></html>"""

@app.route('/', methods=['GET','POST'])
def home():
    if 'used' not in session: session['used'] = 0
    used = session['used']
    is_pro = session.get('is_pro', False)
    if not is_pro and session.get('user_email'):
        is_pro = is_pro_email(session['user_email'])
        if is_pro: session['is_pro'] = True
    limit_reached = (used >= FREE_LIMIT) and not is_pro
    result = error = product = audience = None
    selected_type = 'ad'
    if request.method == 'POST' and not limit_reached:
        product = request.form.get('product','').strip()
        audience = request.form.get('audience','').strip() or 'customers'
        selected_type = request.form.get('copy_type','ad')
        if selected_type not in COPY_TYPES: selected_type = 'ad'
        prompt = COPY_TYPES[selected_type]['prompt'].format(product=product, audience=audience)
        try:
            cc = client.chat.completions.create(messages=[{"role":"user","content":prompt}], model="llama-3.1-8b-instant")
            result = cc.choices[0].message.content
            if not is_pro:
                session['used'] = used + 1
                used = session['used']
                limit_reached = (used >= FREE_LIMIT)
        except Exception as e:
            error = str(e)
    cashapp_url = f"https://cash.app/{CASHAPP_TAG.lstrip('$')}/{CASHAPP_AMOUNT}"
    return render_template_string(HTML, result=result, error=error, product=product, audience=audience,
        selected_type=selected_type, copy_types=COPY_TYPES, used=used, free_limit=FREE_LIMIT,
        limit_reached=limit_reached, is_pro=is_pro, cashapp_tag=CASHAPP_TAG,
        cashapp_amount=CASHAPP_AMOUNT, cashapp_url=cashapp_url,
        crypto_wallets=CRYPTO_WALLETS, promo_error=None)

@app.route('/pay-paystack', methods=['GET','POST'])
def pay_paystack():
    error = email = None
    if request.method == 'POST':
        email = request.form.get('email','').strip()
        if not PAYSTACK_SECRET:
            error = "Paystack not configured. Contact support."
        else:
            ref = make_ref()
            session['pay_ref'] = ref
            session['pay_email'] = email
            save_payment(email, "paystack", f"N{PRO_PRICE_NGN}", ref)
            res = paystack_init(email, PRO_PRICE_NGN * 100, ref)
            if res.get('status'):
                return redirect(res['data']['authorization_url'])
            error = res.get('message','Payment init failed.')
    return render_template_string(PAYSTACK_HTML, error=error, email=email)

@app.route('/verify-paystack')
def verify_paystack():
    ref = request.args.get('reference') or session.get('pay_ref','')
    if ref and PAYSTACK_SECRET:
        res = paystack_verify(ref)
        if res.get('data',{}).get('status') == 'success':
            email = session.get('pay_email','')
            session['is_pro'] = True
            session['used'] = 0
            if email:
                activate_pro_email(email, by="paystack")
                session['user_email'] = email
    return redirect('/')

@app.route('/confirm-crypto', methods=['POST'])
def confirm_crypto():
    email = request.form.get('email','').strip()
    tx_hash = request.form.get('tx_hash','').strip()
    coin = request.form.get('coin','').strip()
    save_payment(email, "crypto", f"~$5 {coin}", tx_hash, coin, "pending")
    session['user_email'] = email
    return render_template_string(PENDING_HTML, email=email, tx_hash=tx_hash)

@app.route('/promo', methods=['POST'])
def promo():
    code = request.form.get('code','').strip().upper()
    if 'used' not in session: session['used'] = 0
    if code in PROMO_CODES:
        session['is_pro'] = True
        session['used'] = 0
        return redirect('/')
    cashapp_url = f"https://cash.app/{CASHAPP_TAG.lstrip('$')}/{CASHAPP_AMOUNT}"
    return render_template_string(HTML, result=None, error=None, product=None, audience=None,
        selected_type='ad', copy_types=COPY_TYPES, used=session['used'], free_limit=FREE_LIMIT,
        limit_reached=True, is_pro=False, cashapp_tag=CASHAPP_TAG, cashapp_amount=CASHAPP_AMOUNT,
        cashapp_url=cashapp_url, crypto_wallets=CRYPTO_WALLETS,
        promo_error="Invalid promo code. Try again.")

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
        stats = {
            "total": db.execute("SELECT COUNT(*) FROM payments").fetchone()[0],
            "pending": db.execute("SELECT COUNT(*) FROM payments WHERE status='pending'").fetchone()[0],
            "activated": db.execute("SELECT COUNT(*) FROM payments WHERE status='activated'").fetchone()[0],
            "pro_count": db.execute("SELECT COUNT(*) FROM pro_users").fetchone()[0],
        }
    flash = session.pop('admin_flash', None)
    return render_template_string(ADMIN_HTML, stats=stats, all_payments=all_payments,
        pending_payments=pending_payments, pending_count=len(pending_payments),
        pro_users=pro_users, flash=flash,
        now=datetime.now().strftime("%A, %d %B %Y - %H:%M"))

@app.route('/admin/activate/<int:payment_id>', methods=['POST'])
@admin_required
def admin_activate(payment_id):
    with get_db() as db:
        row = db.execute("SELECT * FROM payments WHERE id=?", (payment_id,)).fetchone()
        if row:
            activate_pro_email(row['email'], by="admin")
            session['admin_flash'] = f"Pro activated for {row['email']}"
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
    if email:
        save_payment(email, "manual", "$5", "manual-"+make_ref(), "", "activated")
        activate_pro_email(email, by="admin-manual")
        session['admin_flash'] = f"Pro manually activated for {email}"
    return redirect('/admin')

@app.route('/api/check-pro')
def api_check_pro():
    email = request.args.get('email','')
    return jsonify({"pro": is_pro_email(email)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
