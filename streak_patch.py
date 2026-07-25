with open('app.py', 'r') as f:
    content = f.read()

old = '''def deduct_credit(email):
    with get_db() as db:
        row = db.execute("SELECT balance FROM credits WHERE email=?", (email,)).fetchone()
        if not row or row["balance"] <= 0:
            return False
        db.execute("UPDATE credits SET balance = balance - 1 WHERE email=?", (email,))
        db.commit()
    return True'''

new = '''def update_streak(email):
    from datetime import date, timedelta
    today = date.today()
    milestone_hit = None
    bonus_credits = 0

    with get_db() as db:
        row = db.execute("SELECT * FROM user_streaks WHERE user_email=?", (email,)).fetchone()

        if not row:
            db.execute(
                "INSERT INTO user_streaks (user_email, current_streak, longest_streak, last_activity_date, streak_freezes_available) VALUES (?,1,1,?,1)",
                (email, today.isoformat())
            )
            db.commit()
            return {"current_streak": 1, "longest_streak": 1, "milestone_hit": None, "bonus_credits": 0}

        last_date_str = row["last_activity_date"]
        current_streak = row["current_streak"]
        longest_streak = row["longest_streak"]
        freezes = row["streak_freezes_available"]
        last_milestone = row["last_milestone_awarded"]

        last_date = date.fromisoformat(last_date_str) if last_date_str else None

        if last_date == today:
            return {"current_streak": current_streak, "longest_streak": longest_streak, "milestone_hit": None, "bonus_credits": 0}
        elif last_date == today - timedelta(days=1):
            current_streak += 1
        elif last_date is not None and last_date == today - timedelta(days=2) and freezes > 0:
            freezes -= 1
            current_streak += 1
        else:
            current_streak = 1

        longest_streak = max(longest_streak, current_streak)

        milestones = {7: 10, 30: 50, 100: 180}
        if current_streak in milestones and last_milestone < current_streak:
            milestone_hit = current_streak
            bonus_credits = milestones[current_streak]
            db.execute("UPDATE credits SET balance = balance + ? WHERE email=?", (bonus_credits, email))
            last_milestone = current_streak

        db.execute(
            "UPDATE user_streaks SET current_streak=?, longest_streak=?, last_activity_date=?, streak_freezes_available=?, last_milestone_awarded=? WHERE user_email=?",
            (current_streak, longest_streak, today.isoformat(), freezes, last_milestone, email)
        )
        db.commit()

    return {"current_streak": current_streak, "longest_streak": longest_streak, "milestone_hit": milestone_hit, "bonus_credits": bonus_credits}


def deduct_credit(email):
    with get_db() as db:
        row = db.execute("SELECT balance FROM credits WHERE email=?", (email,)).fetchone()
        if not row or row["balance"] <= 0:
            return False
        db.execute("UPDATE credits SET balance = balance - 1 WHERE email=?", (email,))
        db.commit()
    update_streak(email)
    return True'''

if old not in content:
    print("ERROR: pattern not found, no changes made")
else:
    content = content.replace(old, new, 1)
    with open('app.py', 'w') as f:
        f.write(content)
    print("SUCCESS: update_streak function added and hooked into deduct_credit")
