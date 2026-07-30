from pathlib import Path

path = Path("app.py")
text = path.read_text()

old = """        result = cc.choices[0].message.content
        variations = [v.strip() for v in result.split('---') if v.strip()]
"""

new = """        result = cc.choices[0].message.content

        if "###STRATEGY###" in result:
            ad_text, strategy_text = result.split("###STRATEGY###", 1)
        else:
            ad_text = result
            strategy_text = ""

        variations = [v.strip() for v in ad_text.split('---') if v.strip()]

        strategist = {
            "objective": "",
            "recommended_platform": platform,
            "recommended_audience": customer or "General African small business customers",
            "best_posting_time": "",
            "marketing_tip": "",
            "follow_up": "",
            "ab_test": "",
            "ai_strategy": strategy_text.strip(),
        }
"""

if old not in text:
    raise SystemExit("Target block not found.")

path.write_text(text.replace(old, new))

print("✓ Unified AI response patch applied.")
