"""
============================================================
CopySwift AI
Industry Intelligence Engine
Version : 2.2.0-a
============================================================
"""

DEFAULT_PROFILE = {
    "industry": "General Business",
    "description": "General products and services.",
    "pain_points": [
        "Need more customers",
        "Need more sales",
        "Need stronger brand awareness"
    ],
    "benefits": [
        "High quality",
        "Affordable pricing",
        "Trusted service"
    ],
    "keywords": [
        "quality",
        "professional",
        "trusted"
    ],
    "tone": "Professional",
    "cta": "Contact us today."
}


INDUSTRIES = {

    "restaurant": {

        "industry": "Restaurant",

        "description":
        "Restaurants, fast food, cafes and catering businesses.",

        "pain_points": [
            "Hungry customers",
            "Need fast delivery",
            "Affordable meals"
        ],

        "benefits": [
            "Fresh meals",
            "Delicious taste",
            "Fast delivery",
            "Family friendly"
        ],

        "keywords": [
            "fresh",
            "delicious",
            "meal",
            "restaurant",
            "delivery"
        ],

        "tone": "Friendly",

        "cta": "Order now."
    },

    "real_estate": {

        "industry": "Real Estate",

        "description":
        "Property sales, rentals and investment.",

        "pain_points": [
            "Need secure investment",
            "Finding dream home",
            "Affordable property"
        ],

        "benefits": [
            "Prime locations",
            "High investment value",
            "Flexible payment options"
        ],

        "keywords": [
            "property",
            "investment",
            "home",
            "land",
            "real estate"
        ],

        "tone": "Professional",

        "cta": "Book a property inspection today."
    },

    "fashion": {

        "industry": "Fashion",

        "description":
        "Clothing, shoes, bags and accessories.",

        "pain_points": [
            "Looking stylish",
            "Affordable fashion"
        ],

        "benefits": [
            "Latest trends",
            "Premium quality",
            "Affordable prices"
        ],

        "keywords": [
            "fashion",
            "style",
            "premium",
            "clothing"
        ],

        "tone": "Luxury",

        "cta": "Shop the latest collection."
    },

    "healthcare": {

        "industry": "Healthcare",

        "description":
        "Hospitals, clinics and pharmacies.",

        "pain_points": [
            "Need quality healthcare",
            "Reliable medical support"
        ],

        "benefits": [
            "Professional care",
            "Trusted experts",
            "Modern equipment"
        ],

        "keywords": [
            "health",
            "doctor",
            "clinic",
            "care"
        ],

        "tone": "Professional",

        "cta": "Book your appointment today."
    },

    "education": {

        "industry": "Education",

        "description":
        "Schools, colleges and online learning.",

        "pain_points": [
            "Need quality education",
            "Career growth"
        ],

        "benefits": [
            "Expert teachers",
            "Modern learning",
            "Practical skills"
        ],

        "keywords": [
            "education",
            "learning",
            "training"
        ],

        "tone": "Inspirational",

        "cta": "Enroll today."
    },

    "church": {

        "industry": "Church",

        "description":
        "Churches, ministries and Christian organizations.",

        "pain_points": [
            "Need spiritual growth",
            "Need hope",
            "Need prayer"
        ],

        "benefits": [
            "Faith",
            "Community",
            "Biblical teaching"
        ],

        "keywords": [
            "Jesus",
            "faith",
            "church",
            "hope"
        ],

        "tone": "Inspirational",

        "cta": "Join us this Sunday."
    },

    "finance": {

        "industry": "Financial Services",

        "description":
        "Banks, fintech and financial advisors.",

        "pain_points": [
            "Financial security",
            "Saving money",
            "Growing wealth"
        ],

        "benefits": [
            "Trusted advice",
            "Secure services",
            "Professional support"
        ],

        "keywords": [
            "finance",
            "investment",
            "money"
        ],

        "tone": "Professional",

        "cta": "Start your financial journey today."
    },

    "travel": {

        "industry": "Travel",

        "description":
        "Travel agencies, tours and hospitality.",

        "pain_points": [
            "Planning trips",
            "Affordable travel"
        ],

        "benefits": [
            "Amazing destinations",
            "Comfort",
            "Affordable packages"
        ],

        "keywords": [
            "travel",
            "holiday",
            "tour"
        ],

        "tone": "Exciting",

        "cta": "Book your trip today."
    },

    "agriculture": {

        "industry": "Agriculture",

        "description":
        "Farming and agribusiness.",

        "pain_points": [
            "Increase yield",
            "Modern farming"
        ],

        "benefits": [
            "Better productivity",
            "Reliable support",
            "Quality produce"
        ],

        "keywords": [
            "farm",
            "agriculture",
            "harvest"
        ],

        "tone": "Professional",

        "cta": "Grow with us today."
    },

    "ecommerce": {

        "industry": "E-Commerce",

        "description":
        "Online stores and digital commerce.",

        "pain_points": [
            "Need online sales",
            "Need repeat customers"
        ],

        "benefits": [
            "Fast delivery",
            "Secure shopping",
            "Best prices"
        ],

        "keywords": [
            "online",
            "shopping",
            "discount"
        ],

        "tone": "Persuasive",

        "cta": "Buy now."
    }

}


def get_industry_profile(industry):

    if not industry:
        return DEFAULT_PROFILE

    key = industry.strip().lower().replace(" ", "_")

    return INDUSTRIES.get(key, DEFAULT_PROFILE)


if __name__ == "__main__":

    print("=" * 60)
    print("CopySwift AI Industry Intelligence Engine")
    print("=" * 60)

    profile = get_industry_profile("restaurant")

    print()
    print("Industry :", profile["industry"])
    print("Tone     :", profile["tone"])
    print("CTA      :", profile["cta"])
