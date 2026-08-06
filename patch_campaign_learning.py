from pathlib import Path

path = Path("app.py")
text = path.read_text()

marker = "def update_business_profile(email, profile_id, business_name, product, audience, tone):"

helper = '''

def save_campaign_learning(email, headlines, cta, objection):
    """Persist simple campaign learnings for the active business profile."""
    if not email:
        return

    with get_db() as db:
        profile = db.execute(
            "SELECT id FROM business_profiles WHERE email=? AND is_active=1",
            (email,)
        ).fetchone()

        if not profile:
            return

        db.execute("""
            UPDATE business_profiles
            SET
                winning_headlines = COALESCE(winning_headlines,'') || ? || char(10),
                winning_ctas = COALESCE(winning_ctas,'') || ? || char(10),
                customer_objections = COALESCE(customer_objections,'') || ? || char(10)
            WHERE id=?
        """, (
            headlines,
            cta,
            objection,
            profile["id"]
        ))

        db.commit()

'''

if helper in text:
    print("Already installed.")
    raise SystemExit()

idx = text.find(marker)
if idx == -1:
    raise SystemExit("Insertion point not found.")

text = text[:idx] + helper + text[idx:]

path.write_text(text)

print("✓ Campaign learning helper added.")
