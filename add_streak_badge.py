with open('app.py', 'r') as f:
    content = f.read()

old = '''  <a href="#upgrade" class="upgrade-link">Buy Credits →</a>
</div>
{% if credits_balance > 0 %}'''

new = '''  <a href="#upgrade" class="upgrade-link">Buy Credits →</a>
</div>
{% if streak_current and streak_current > 0 %}
<div class="usage-bar" style="background:linear-gradient(135deg,rgba(255,107,53,0.15),rgba(247,147,30,0.1));border:1px solid rgba(255,107,53,0.3);margin-top:10px">
  <span class="usage-label">🔥 {{ streak_current }}-day streak</span>
  <div class="usage-dots">
    <span style="color:var(--muted);font-size:12px">Best: {{ streak_longest }} days</span>
  </div>
</div>
{% endif %}
{% if credits_balance > 0 %}'''

if old not in content:
    print("ERROR: pattern not found")
else:
    content = content.replace(old, new, 1)
    with open('app.py', 'w') as f:
        f.write(content)
    print("SUCCESS: streak badge HTML added")
