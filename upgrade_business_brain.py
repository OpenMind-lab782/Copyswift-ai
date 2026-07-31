import sqlite3

db = sqlite3.connect("copyswift.db")

columns = {
    "winning_headlines": "TEXT",
    "winning_ctas": "TEXT",
    "customer_objections": "TEXT",
    "marketing_notes": "TEXT",
    "seasonal_campaigns": "TEXT",
    "last_campaign_summary": "TEXT"
}

existing = {
    row[1]
    for row in db.execute("PRAGMA table_info(business_profiles)")
}

for name, typ in columns.items():
    if name not in existing:
        db.execute(
            f"ALTER TABLE business_profiles ADD COLUMN {name} {typ}"
        )
        print(f"Added {name}")

db.commit()
db.close()

print("✓ AI Business Brain upgraded.")
