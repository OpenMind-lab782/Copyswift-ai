"""
============================================================
CopySwift AI
Tone Intelligence Engine
Version : 2.2.0-b
============================================================
"""

DEFAULT_TONE = {
    "name": "Professional",
    "description": "Clear, trustworthy and business-focused.",
    "style": "Use clear language with a confident and respectful tone.",
    "emotion": "Confidence"
}

TONES = {

    "professional": {
        "name": "Professional",
        "description": "Suitable for businesses and corporate communication.",
        "style": "Be clear, factual and trustworthy.",
        "emotion": "Confidence"
    },

    "friendly": {
        "name": "Friendly",
        "description": "Warm, conversational and approachable.",
        "style": "Use simple language that feels welcoming.",
        "emotion": "Warmth"
    },

    "persuasive": {
        "name": "Persuasive",
        "description": "Encourage readers to take action.",
        "style": "Highlight benefits and urgency while remaining credible.",
        "emotion": "Motivation"
    },

    "luxury": {
        "name": "Luxury",
        "description": "Elegant, premium and exclusive.",
        "style": "Use refined vocabulary that reflects quality and prestige.",
        "emotion": "Exclusivity"
    },

    "inspirational": {
        "name": "Inspirational",
        "description": "Encourage hope, vision and positive action.",
        "style": "Use uplifting language that motivates readers.",
        "emotion": "Hope"
    },

    "urgent": {
        "name": "Urgent",
        "description": "Create a sense of timely action.",
        "style": "Use concise language with clear deadlines or limited availability.",
        "emotion": "Urgency"
    },

    "confident": {
        "name": "Confident",
        "description": "Strong and authoritative.",
        "style": "Write with certainty while avoiding exaggeration.",
        "emotion": "Authority"
    },

    "empathetic": {
        "name": "Empathetic",
        "description": "Show understanding of customer challenges.",
        "style": "Acknowledge pain points before presenting solutions.",
        "emotion": "Empathy"
    },

    "conversational": {
        "name": "Conversational",
        "description": "Natural and easy to read.",
        "style": "Write as though speaking directly to one person.",
        "emotion": "Connection"
    },

    "bold": {
        "name": "Bold",
        "description": "Attention-grabbing and energetic.",
        "style": "Use impactful wording while staying truthful.",
        "emotion": "Excitement"
    }

}

def get_tone_profile(tone):

    if not tone:
        return DEFAULT_TONE

    key = tone.strip().lower().replace(" ", "_")

    return TONES.get(key, DEFAULT_TONE)


if __name__ == "__main__":

    print("=" * 60)
    print("CopySwift AI Tone Intelligence Engine")
    print("=" * 60)

    profile = get_tone_profile("luxury")

    print()
    print("Tone      :", profile["name"])
    print("Emotion   :", profile["emotion"])
    print("Style     :", profile["style"])
