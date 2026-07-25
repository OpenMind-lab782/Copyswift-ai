"""
============================================================
CopySwift AI
Audience Intelligence Engine
Version : 2.2.0-c
============================================================
"""

DEFAULT_AUDIENCE = {
    "name": "General Audience",
    "description": "Suitable for a broad audience.",
    "pain_points": [
        "Need better solutions",
        "Want value for money"
    ],
    "motivations": [
        "Quality",
        "Trust",
        "Convenience"
    ],
    "style": "Use clear and easy-to-understand language."
}

AUDIENCES = {

    "entrepreneurs": {
        "name": "Entrepreneurs",
        "description": "Business owners focused on growth.",
        "pain_points": [
            "Getting customers",
            "Increasing sales",
            "Saving time"
        ],
        "motivations": [
            "Business growth",
            "Profit",
            "Automation"
        ],
        "style": "Results-driven and practical."
    },

    "small_business": {
        "name": "Small Business Owners",
        "description": "Owners of local and growing businesses.",
        "pain_points": [
            "Limited budget",
            "Competition",
            "Marketing"
        ],
        "motivations": [
            "Affordable growth",
            "Customer loyalty"
        ],
        "style": "Friendly, encouraging and practical."
    },

    "students": {
        "name": "Students",
        "description": "Learners seeking education and skills.",
        "pain_points": [
            "Learning",
            "Exams",
            "Career preparation"
        ],
        "motivations": [
            "Success",
            "Knowledge",
            "Opportunities"
        ],
        "style": "Simple, motivating and engaging."
    },

    "parents": {
        "name": "Parents",
        "description": "Parents making decisions for their families.",
        "pain_points": [
            "Child safety",
            "Education",
            "Family wellbeing"
        ],
        "motivations": [
            "Security",
            "Trust",
            "Value"
        ],
        "style": "Warm and reassuring."
    },

    "church_members": {
        "name": "Church Members",
        "description": "People seeking spiritual encouragement.",
        "pain_points": [
            "Need hope",
            "Need encouragement",
            "Need prayer"
        ],
        "motivations": [
            "Faith",
            "Community",
            "Purpose"
        ],
        "style": "Inspirational and compassionate."
    },

    "corporate": {
        "name": "Corporate Executives",
        "description": "Professional business decision-makers.",
        "pain_points": [
            "Efficiency",
            "Risk management",
            "Growth"
        ],
        "motivations": [
            "Performance",
            "Innovation",
            "Leadership"
        ],
        "style": "Professional and authoritative."
    }

}

def get_audience_profile(audience):

    if not audience:
        return DEFAULT_AUDIENCE

    key = audience.strip().lower().replace(" ", "_")

    return AUDIENCES.get(key, DEFAULT_AUDIENCE)


if __name__ == "__main__":

    print("=" * 60)
    print("CopySwift AI Audience Intelligence Engine")
    print("=" * 60)

    profile = get_audience_profile("entrepreneurs")

    print()
    print("Audience    :", profile["name"])
    print("Style       :", profile["style"])
    print("Motivation  :", ", ".join(profile["motivations"]))
