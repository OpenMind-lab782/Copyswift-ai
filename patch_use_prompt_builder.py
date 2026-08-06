from pathlib import Path

path = Path("app.py")
text = path.read_text()

old = '''    prompt = (
'''

if old not in text:
    raise SystemExit("Prompt construction not found.")

start = text.index(old)
end = text.index('    client.chat.completions.create(', start)

replacement = '''    prompt = build_prompt(profile, user_prompt)

'''

text = text[:start] + replacement + text[end:]

path.write_text(text)

print("✓ Prompt Builder integrated.")
