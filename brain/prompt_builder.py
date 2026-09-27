"""
Prompt Builder
"""

from ecosystem_core.market_intelligence.engines import MemoryEngine
from ecosystem_core.market_intelligence.domains.marketing import (
    MARKETING_MEMORY_SCHEMA,
)

_memory_engine = MemoryEngine(schema=MARKETING_MEMORY_SCHEMA)


def build_prompt(profile, offer, customer, hesitation, platform, tone):
    memory = _memory_engine.format_context(profile)

    return f"""{memory}

You are generating marketing copy from supplied business information.
FACTUAL-GROUNDING RULE:
- Treat only the supplied business/profile information below as business facts.
- Never invent or assume a phone number, email address, URL, price, discount,
  coupon code, promotion, guarantee, testimonial, review, rating, customer quote,
  location, opening hours, delivery time, availability, certification, statistic,
  quantity, or performance result.
- Do not turn a marketing suggestion into an existing business fact.
- If a fact is not supplied, omit it.
- A generic call to action such as "Message us to learn more" is allowed.
- Persuasive wording is allowed only when it does not introduce unsupported facts.

Write 3 short ad copy variations for {platform}, in a {tone} tone.

What's being sold:
{offer}

Target customer:
{customer or "General African small business customers"}

Main hesitation to overcome:
{hesitation or "None specified"}

Requirements:

- Produce exactly 3 variations.
- Separate each variation with ---
- Each variation must be under 60 words.
- Each variation must contain:
  - Hook
  - Main benefit
  - Clear call-to-action

After the three variations write exactly:

###STRATEGY###

Then provide:

Objective:
Best Platform:
Best Posting Time:
Marketing Tip:
Follow-up Campaign:
A/B Test:

Output plain text only.
Do not use Markdown.
"""
