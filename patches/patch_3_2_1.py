PATCH_ID = "3.2.1"
DESCRIPTION = "Integrate Resend email after successful Paystack verification."


IMPORT_LINE = "from email_service import send_email"

EMAIL_BLOCK = '''
            try:
                send_email(
                    email,
                    "Payment Successful - CopySwift AI™",
                    f"""
                    <h2>Payment Successful</h2>
                    <p>Hello,</p>
                    <p>Your payment has been received successfully.</p>
                    <p>Your AI credits have been activated and are now available in your account.</p>
                    <hr>
                    <p><b>Thank you for choosing CopySwift AI™.</b></p>
                    """
                )
            except Exception as e:
                print(f"[Email] {e}")
'''


def apply(app_text):
    changes = []

    if IMPORT_LINE not in app_text:
        lines = app_text.splitlines()
        insert_at = 0
        for i, line in enumerate(lines):
            if line.startswith("import ") or line.startswith("from "):
                insert_at = i + 1
        lines.insert(insert_at, IMPORT_LINE)
        app_text = "\n".join(lines)
        changes.append("Added email_service import.")

    if EMAIL_BLOCK.strip() not in app_text:
        target = """            if email:
                session['user_email'] = email"""
        replacement = """            if email:
                session['user_email'] = email
""" + EMAIL_BLOCK.rstrip()

        if target in app_text:
            app_text = app_text.replace(target, replacement, 1)
            changes.append("Integrated Paystack success email.")

    return app_text, changes
