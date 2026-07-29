from payment_engine.api.app import app

print("=== Registered Routes ===")
for rule in sorted(app.url_map.iter_rules(), key=lambda r: r.rule):
    methods = ",".join(sorted(rule.methods - {"HEAD", "OPTIONS"}))
    print(f"{rule.rule:30} {methods:10} -> {rule.endpoint}")
