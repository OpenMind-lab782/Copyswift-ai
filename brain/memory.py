"""
Business Memory Engine
"""

def load_business_memory(profile):
    if not profile:
        return ""

    sections = []

    mapping = [
        ("Brand Voice", "brand_voice"),
        ("Brand Style", "brand_style"),
        ("Business Goal", "brand_goal"),
        ("Keywords", "brand_keywords"),
        ("CTA", "brand_cta"),
        ("Winning Headlines", "winning_headlines"),
        ("Winning CTAs", "winning_ctas"),
        ("Customer Objections", "customer_objections"),
        ("Marketing Notes", "marketing_notes"),
        ("Seasonal Campaigns", "seasonal_campaigns"),
        ("Last Campaign", "last_campaign_summary"),
    ]

    for title, key in mapping:
        value = profile.get(key)
        if value:
            sections.append(f"{title}: {value}")

    return "\n".join(sections)
