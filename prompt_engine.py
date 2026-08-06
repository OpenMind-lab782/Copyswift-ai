"""
============================================================
CopySwift AI Prompt Engine
Version : 3.1.0
============================================================
"""

from industry_profiles import get_industry_profile
from tone_profiles import get_tone_profile
from audience_profiles import get_audience_profile

PROMPT_TEMPLATE = """
You are CopySwift AI, an expert marketing strategist and copywriter.

Business/Product:
{product}

Industry Intelligence
---------------------
Industry: {industry}
Description: {industry_description}

Industry Pain Points:
{industry_pain_points}

Industry Benefits:
{industry_benefits}

Industry Keywords:
{industry_keywords}

Audience Intelligence
---------------------
Audience: {audience}
Audience Description:
{audience_description}

Audience Pain Points:
{audience_pain_points}

Audience Motivations:
{audience_motivations}

Tone Intelligence
-----------------
Tone:
{tone}

Writing Style:
{tone_style}

Emotional Direction:
{tone_emotion}

Campaign Details
----------------
Country: {country}
Language: {language}
Platform: {platform}
Goal: {goal}
Offer: {offer}

Customer Problem:
{problem}

Customer Desire:
{desire}

Customer Objection:
{objection}

Instructions
------------
1. Use AIDA.
2. Use PAS where appropriate.
3. Focus on benefits, not just features.
4. Speak naturally to customers in {country}.
5. Match the requested tone.
6. Address audience motivations.
7. Address objections naturally.
8. Include a clear and persuasive call to action.
9. Do not use Markdown.
10. Return only the final marketing copy.
"""

def build_prompt(
    product,
    industry="general",
    audience="general",
    tone="professional",
    country="",
    language="English",
    platform="General",
    goal="Generate sales",
    problem="",
    desire="",
    objection="",
    offer=""
):
    industry_profile = get_industry_profile(industry)
    tone_profile = get_tone_profile(tone)
    audience_profile = get_audience_profile(audience)

    return PROMPT_TEMPLATE.format(
        product=product,

        industry=industry_profile["industry"],
        industry_description=industry_profile["description"],
        industry_pain_points=", ".join(industry_profile["pain_points"]),
        industry_benefits=", ".join(industry_profile["benefits"]),
        industry_keywords=", ".join(industry_profile["keywords"]),

        audience=audience_profile["name"],
        audience_description=audience_profile["description"],
        audience_pain_points=", ".join(audience_profile["pain_points"]),
        audience_motivations=", ".join(audience_profile["motivations"]),

        tone=tone_profile["name"],
        tone_style=tone_profile["style"],
        tone_emotion=tone_profile["emotion"],

        country=country,
        language=language,
        platform=platform,
        goal=goal,
        offer=offer,
        problem=problem,
        desire=desire,
        objection=objection
    )

def validate_prompt(prompt):
    if not prompt:
        return False

    if len(prompt.strip()) < 100:
        return False

    return True

if __name__ == "__main__":

    prompt = build_prompt(
        product="AI Marketing Software",
        industry="technology",
        audience="entrepreneurs",
        tone="professional",
        country="Botswana",
        language="English",
        platform="Facebook",
        goal="Generate Leads",
        problem="Low sales",
        desire="More customers",
        objection="Price",
        offer="Free Trial"
    )

    print("=" * 60)
    print("CopySwift AI Prompt Engine v3.1")
    print("=" * 60)
    print(prompt[:1200])
    print()
    print("Prompt Valid:", validate_prompt(prompt))
