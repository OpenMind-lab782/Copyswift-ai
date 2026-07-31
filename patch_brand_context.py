from pathlib import Path

path = Path("app.py")
text = path.read_text()

old = """    prompt = (
        f"Write 3 short ad copy variations for {platform}, in a {tone} tone.\\n"
        f"What's being sold: {offer}\\n"
        f"Target customer: {customer or 'general African small business customers'}\\n"
        f"Their main hesitation to address: {hesitation or 'none specified'}\\n"
        f"Each variation must be under 60 words, include a hook, the pitch, and a clear call-to-action. "
        f"Separate the 3 variations with '---'. Write in plain text only — no Markdown, no **, no ## headers, no bullet symbols."
    )
"""

new = """    profile = get_active_business_profile(session.get("user_email"))

    brand_context = ""
    if profile:
        brand_context = (
            f"Business Name: {profile.get('business_name','')}\\n"
            f"Product: {profile.get('product','')}\\n"
            f"Audience: {profile.get('audience','')}\\n"
            f"Brand Voice: {profile.get('brand_voice','Professional')}\\n"
            f"Brand Style: {profile.get('brand_style','Modern')}\\n"
            f"Business Goal: {profile.get('brand_goal','Sales')}\\n"
            f"Brand Keywords: {profile.get('brand_keywords','')}\\n"
            f"Preferred CTA: {profile.get('brand_cta','Order Now')}\\n\\n"
        )

    prompt = (
        brand_context +
        f"Write 3 short ad copy variations for {platform}, in a {tone} tone.\\n"
        f"What's being sold: {offer}\\n"
        f"Target customer: {customer or 'general African small business customers'}\\n"
        f"Their main hesitation to address: {hesitation or 'none specified'}\\n"
        f"Each variation must be under 60 words, include a hook, the pitch, and a clear call-to-action. "
        f"Separate the 3 variations with '---'. Write in plain text only — no Markdown, no **, no ## headers, no bullet symbols."
    )
"""

if old not in text:
    raise SystemExit("Prompt block not found.")

path.write_text(text.replace(old, new))

print("✓ Brand Context AI upgraded.")
