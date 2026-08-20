"""
CopySwiftAI™ SEO Agent Foundation.
"""


class SEOAgent:
    """Initial shared-kernel SEO analysis component."""

    def __init__(self, provider=None):
        self.provider = provider

    def analyze(self, keyword, content):
        keyword_text = (keyword or "").strip()
        content_text = (content or "").strip()

        normalized_keyword = keyword_text.lower()
        normalized_content = content_text.lower()

        words = normalized_content.split()
        keyword_present = bool(
            normalized_keyword
            and normalized_keyword in normalized_content
        )

        score = 100
        recommendations = []

        if not content_text:
            score = 0
            recommendations.append(
                "Add substantive content for SEO analysis."
            )
        else:
            if not keyword_present:
                score -= 30
                recommendations.append(
                    "Include the target keyword naturally in the content."
                )

            if len(words) < 30:
                score -= 20
                recommendations.append(
                    "Expand the content with more useful topical coverage."
                )

            if keyword_present and len(words) >= 30:
                recommendations.append(
                    "Maintain natural keyword usage and topical relevance."
                )

        score = max(0, min(100, score))

        return {
            "keyword": keyword_text,
            "score": score,
            "recommendations": recommendations,
        }


    def analyze_page(
        self,
        url,
        title,
        headings,
        content,
        target_keyword,
    ):
        """Perform deterministic on-page SEO foundation analysis."""

        url_text = (url or "").strip()
        title_text = (title or "").strip()
        content_text = (content or "").strip()
        keyword_text = (target_keyword or "").strip()

        heading_values = [
            str(heading).strip()
            for heading in (headings or [])
            if str(heading).strip()
        ]

        keyword = keyword_text.lower()
        title_lower = title_text.lower()
        headings_lower = [
            heading.lower()
            for heading in heading_values
        ]

        checks = {}

        title_has_keyword = bool(
            keyword and keyword in title_lower
        )
        heading_has_keyword = bool(
            keyword
            and any(keyword in heading for heading in headings_lower)
        )
        content_has_keyword = bool(
            keyword
            and keyword in content_text.lower()
        )

        checks["title"] = {
            "keyword_present": title_has_keyword,
            "passed": bool(title_text and title_has_keyword),
        }

        checks["headings"] = {
            "keyword_present": heading_has_keyword,
            "heading_count": len(heading_values),
            "passed": bool(heading_values and heading_has_keyword),
        }

        checks["content"] = {
            "keyword_present": content_has_keyword,
            "word_count": len(content_text.split()),
            "passed": bool(content_text and content_has_keyword),
        }

        score = 0

        if checks["title"]["passed"]:
            score += 35

        if checks["headings"]["passed"]:
            score += 30

        if checks["content"]["passed"]:
            score += 35

        recommendations = []

        if not checks["title"]["passed"]:
            recommendations.append(
                "Include the target keyword naturally in the page title."
            )

        if not checks["headings"]["passed"]:
            recommendations.append(
                "Include the target keyword naturally in at least one heading."
            )

        if not checks["content"]["passed"]:
            recommendations.append(
                "Include the target keyword naturally in the page content."
            )

        if not content_text:
            recommendations.append(
                "Add substantive content for SEO analysis."
            )

        return {
            "url": url_text,
            "keyword": keyword_text,
            "score": score,
            "checks": checks,
            "recommendations": recommendations,
        }


    def analyze_keywords(self, seed_keyword):
        """Generate deterministic keyword opportunities from a seed term."""

        seed = (seed_keyword or "").strip()

        if not seed:
            return {
                "seed_keyword": "",
                "keywords": [],
                "clusters": {},
                "recommendations": [
                    "Provide a seed keyword for SEO research."
                ],
            }

        base = seed.lower()

        candidates = [
            (base, "informational", 85),
            (f"{base} tools", "commercial", 90),
            (f"{base} software", "commercial", 88),
            (f"best {base}", "commercial", 92),
            (f"{base} for small business", "commercial", 86),
            (f"how to use {base}", "informational", 80),
            (f"{base} examples", "informational", 78),
            (f"free {base}", "transactional", 82),
        ]

        keywords = [
            {
                "keyword": keyword,
                "intent": intent,
                "opportunity": opportunity,
            }
            for keyword, intent, opportunity in candidates
        ]

        clusters = {
            "core": [base],
            "commercial": [
                keyword
                for keyword, intent, _ in candidates
                if intent == "commercial"
            ],
            "informational": [
                keyword
                for keyword, intent, _ in candidates
                if intent == "informational"
            ],
            "transactional": [
                keyword
                for keyword, intent, _ in candidates
                if intent == "transactional"
            ],
        }

        recommendations = [
            "Prioritize commercial keywords for conversion-focused pages.",
            "Use informational keywords for educational content.",
            "Create content clusters around the strongest related opportunities.",
        ]

        return {
            "seed_keyword": seed,
            "keywords": keywords,
            "clusters": clusters,
            "recommendations": recommendations,
        }


    def analyze_content(self, keyword, content):
        """Perform deterministic content-quality SEO analysis."""

        keyword_text = (keyword or "").strip()
        content_text = (content or "").strip()

        normalized_keyword = keyword_text.lower()
        normalized_content = content_text.lower()

        words = normalized_content.split()

        keyword_occurrences = (
            normalized_content.count(normalized_keyword)
            if normalized_keyword
            else 0
        )

        word_count = len(words)

        keyword_density = (
            (keyword_occurrences / word_count) * 100
            if word_count and keyword_occurrences
            else 0
        )

        paragraphs = [
            paragraph.strip()
            for paragraph in content_text.split("\n\n")
            if paragraph.strip()
        ]

        sentence_count = sum(
            1
            for sentence in (
                content_text.replace("!", ".")
                .replace("?", ".")
                .split(".")
            )
            if sentence.strip()
        )

        paragraph_count = len(paragraphs)

        score = 100
        recommendations = []

        if not content_text:
            score = 0
            recommendations.append(
                "Add substantive content for SEO analysis."
            )
        else:
            if not keyword_text:
                score -= 20
                recommendations.append(
                    "Provide a target keyword for content analysis."
                )

            if word_count < 30:
                score -= 20
                recommendations.append(
                    "Expand the content with more useful topical coverage."
                )

            if keyword_text and keyword_occurrences == 0:
                score -= 30
                recommendations.append(
                    "Include the target keyword naturally in the content."
                )

            if keyword_occurrences and keyword_density > 3:
                score -= 10
                recommendations.append(
                    "Reduce excessive keyword repetition and keep usage natural."
                )

        score = max(0, min(100, score))

        return {
            "keyword": keyword_text,
            "word_count": word_count,
            "keyword_occurrences": keyword_occurrences,
            "keyword_density": round(keyword_density, 2),
            "paragraph_count": paragraph_count,
            "sentence_count": sentence_count,
            "score": score,
            "recommendations": recommendations,
        }


    def optimize_content(self, keyword, content):
        """Perform deterministic SEO content optimization."""
        keyword_text = (keyword or "").strip()
        content_text = (content or "").strip()
        original_analysis = self.analyze_content(keyword=keyword_text, content=content_text)
        optimized_content = content_text
        changes = []
        recommendations = []
        if not content_text:
            if keyword_text:
                optimized_content = keyword_text
                changes.append("Added the target keyword because the source content was empty.")
            else:
                recommendations.append("Provide content and a target keyword for meaningful optimization.")
        elif keyword_text and keyword_text.lower() not in content_text.lower():
            optimized_content = f"{keyword_text.title()} is an important topic for businesses. {content_text}"
            changes.append("Added the target keyword naturally to improve keyword coverage.")
        else:
            changes.append("Retained the existing keyword coverage because the target keyword is already present.")
        optimized_analysis = self.analyze_content(keyword=keyword_text, content=optimized_content)
        if optimized_analysis["word_count"] < 30:
            recommendations.append("Expand the optimized content with more useful topical coverage.")
        if keyword_text and optimized_analysis["keyword_occurrences"] == 0:
            recommendations.append("Include the target keyword naturally in the optimized content.")
        if optimized_analysis["keyword_density"] > 3:
            recommendations.append("Review keyword repetition and keep usage natural.")
        return {"keyword": keyword_text, "original_content": content_text, "optimized_content": optimized_content, "original_analysis": original_analysis, "optimized_analysis": optimized_analysis, "changes": changes, "recommendations": recommendations}

    def build_content_strategy(self, seed_keyword):
        """Build a deterministic SEO content strategy from a seed keyword."""

        seed = (seed_keyword or "").strip()

        if not seed:
            return {
                "seed_keyword": "",
                "pillars": [],
                "content_plan": [],
                "recommendations": [
                    "Provide a seed keyword before building a content strategy."
                ],
            }

        keyword_data = self.analyze_keywords(seed)
        base = seed.lower()

        pillars = [
            f"{seed.title()} Fundamentals",
            f"{seed.title()} Tools and Solutions",
            f"{seed.title()} Strategies and Best Practices",
            f"{seed.title()} Use Cases",
        ]

        content_plan = [
            {
                "title": f"What Is {seed.title()}?",
                "keyword": base,
                "intent": "informational",
                "content_type": "pillar",
            },
            {
                "title": f"Best {seed.title()} Tools for Businesses",
                "keyword": f"{base} tools",
                "intent": "commercial",
                "content_type": "comparison",
            },
            {
                "title": f"How to Use {seed.title()} Effectively",
                "keyword": f"how to use {base}",
                "intent": "informational",
                "content_type": "how_to",
            },
            {
                "title": f"{seed.title()} Examples and Use Cases",
                "keyword": f"{base} examples",
                "intent": "informational",
                "content_type": "guide",
            },
            {
                "title": f"Best {seed.title()} Software",
                "keyword": f"{base} software",
                "intent": "commercial",
                "content_type": "comparison",
            },
            {
                "title": f"Free {seed.title()} Options",
                "keyword": f"free {base}",
                "intent": "transactional",
                "content_type": "landing_page",
            },
        ]

        recommendations = [
            "Publish the pillar topic before supporting cluster content.",
            "Link supporting articles back to the primary pillar.",
            "Prioritize commercial topics near conversion-focused pages.",
            "Use informational content to build topical authority.",
        ]

        return {
            "seed_keyword": seed,
            "pillars": pillars,
            "content_plan": content_plan,
            "keyword_data": keyword_data,
            "recommendations": recommendations,
        }


    def build_content_brief(self, keyword):
        """Build a deterministic SEO content brief for a target keyword."""

        target = (keyword or "").strip()

        if not target:
            return {
                "keyword": "",
                "search_intent": "unknown",
                "title": "",
                "outline": [],
                "key_points": [],
                "internal_link_topics": [],
            }

        normalized = target.lower()

        if normalized.startswith(("how ", "what ", "why ", "guide")):
            intent = "informational"
        elif normalized.startswith(("best ", "top ")) or "tools" in normalized:
            intent = "commercial"
        elif normalized.startswith(("buy ", "free ")):
            intent = "transactional"
        else:
            intent = "mixed"

        title = f"Best {target.title()} for Businesses"

        outline = [
            f"Introduction to {target.title()}",
            f"Why {target.title()} Matters",
            f"Key Features of {target.title()}",
            f"How to Choose {target.title()}",
            f"Best Practices for Using {target.title()}",
            f"Frequently Asked Questions About {target.title()}",
        ]

        key_points = [
            f"Define {target} clearly for the reader.",
            f"Explain the main benefits of {target}.",
            f"Address practical considerations when evaluating {target}.",
            f"Provide actionable guidance related to {target}.",
        ]

        internal_link_topics = [
            f"{target} guide",
            f"{target} examples",
            f"{target} tools",
            f"{target} best practices",
        ]

        return {
            "keyword": target,
            "search_intent": intent,
            "title": title,
            "outline": outline,
            "key_points": key_points,
            "internal_link_topics": internal_link_topics,
        }
