"""CopySwiftAI SEO industry content layer."""

SEO_INDUSTRY_CONTENT = {}

def get_seo_industry_content(slug):
    return SEO_INDUSTRY_CONTENT.get(slug, {})
