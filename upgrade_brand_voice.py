import sqlite3

db = sqlite3.connect("copyswift.db")
cur = db.cursor()

columns = {
    "brand_voice": "TEXT DEFAULT 'Professional'",
    "brand_style": "TEXT DEFAULT 'Modern'",
    "brand_goal": "TEXT DEFAULT 'Sales'",
    "brand_keywords": "TEXT DEFAULT ''",
    "brand_cta": "TEXT DEFAULT 'Order Now'"
}

existing = {
    row[1]
    for row in cur.execute("PRAGMA table_info(business_profiles)")
}

for name, definition in columns.items():
    if name not in existing:
        cur.execute(
            f"ALTER TABLE business_profiles ADD COLUMN {name} {definition}"
        )
        print(f"✓ Added {name}")
    else:
        print(f"✓ {name} already exists")

db.commit()
db.close()

print("Brand Voice upgrade completed.")
