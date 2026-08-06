from pathlib import Path

path = Path("app.py")
text = path.read_text()

old = """    return jsonify({
        "variations": variations,
        "remaining_uses": _ad_copy_remaining_uses(),
    })
"""

new = """    strategist = {
        "objective": "Increase conversions",
        "recommended_platform": platform,
        "recommended_audience": customer or "General African small business customers",
        "best_posting_time": "09:00-11:00 or 18:00-21:00",
        "marketing_tip": "Reply to every interested customer within 5 minutes for higher conversion.",
        "follow_up": "Republish the best-performing variation after 48 hours.",
        "ab_test": "Test variation 1 against variation 2 and compare engagement."
    }

    return jsonify({
        "variations": variations,
        "strategist": strategist,
        "remaining_uses": _ad_copy_remaining_uses(),
    })
"""

if old not in text:
    raise SystemExit("Return block not found.")

path.write_text(text.replace(old, new))

print("✓ AI Marketing Strategist added.")
