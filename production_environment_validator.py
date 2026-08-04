import os
import secrets

print("=" * 72)
print("Swift Payment Engine Production Environment Validator")
print("=" * 72)

required = [
    "SECRET_KEY",
    "GROQ_API_KEY",
]

optional = [
    "PAYSTACK_SECRET_KEY",
    "FLUTTERWAVE_SECRET_KEY",
    "STRIPE_SECRET_KEY",
]

print("\nRequired Variables")
print("-" * 72)

missing = []

for key in required:
    value = os.environ.get(key)

    if value:
        print(f"PASS - {key}")
    else:
        print(f"FAIL - {key}")
        missing.append(key)

print("\nOptional Variables")
print("-" * 72)

for key in optional:
    if os.environ.get(key):
        print(f"PASS - {key}")
    else:
        print(f"INFO - {key} not configured")

print("\nSuggested SECRET_KEY")
print("-" * 72)

print(secrets.token_urlsafe(64))

print("\n" + "=" * 72)

if missing:
    print("ENVIRONMENT NOT YET COMPLETE")
else:
    print("ENVIRONMENT READY FOR RENDER")

print("=" * 72)
