from __future__ import annotations

SEO_CONTENT_FIELDS = ("intro", "angles", "objections", "tips")

def validate_seo_industry_content(content):
    if not isinstance(content, dict):
        return False
    if any(field not in content for field in SEO_CONTENT_FIELDS):
        return False
    return (
        isinstance(content["intro"], str)
        and len(content["intro"].strip()) >= 80
        and all(isinstance(items, list) and len(items) == 3 and all(isinstance(item, str) and item.strip() for item in items) for items in (content["angles"], content["objections"], content["tips"]))
    )

SEO_INDUSTRY_CONTENT = {
    "fashion-retail": {
        "intro": "Fashion and Ankara retailers compete on style, trust, fit, price, and delivery speed. Your ad copy should help shoppers picture the outfit, understand the offer quickly, and know exactly how to order, rather than relying on generic claims about quality or beauty.",
        "angles": [
            "Show the occasion: position the outfit around weddings, weekends, workwear, celebrations, or everyday style.",
            "Lead with the offer: make price, availability, sizing, delivery area, or made-to-order details easy to spot.",
            "Use visual proof: highlight fabric details, customer photos, craftsmanship, new arrivals, or before-and-after styling ideas."
        ],
        "objections": [
            "Will the outfit fit me and look like the picture?",
            "Is the fabric or workmanship really worth the price?",
            "Will my order arrive on time and in good condition?"
        ],
        "tips": [
            "Pair every promotional claim with one concrete detail such as fabric, size range, price, location, or delivery promise.",
            "Use short hooks for WhatsApp Status, but add more product proof and context for Facebook and Instagram.",
            "Test two or three different hooks around the same product so you learn whether price, occasion, proof, or scarcity drives more enquiries."
        ]
    }
}


def get_seo_industry_content(slug):
    return SEO_INDUSTRY_CONTENT.get(slug, {})
