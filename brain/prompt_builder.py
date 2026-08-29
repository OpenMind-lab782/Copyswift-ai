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
