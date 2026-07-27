PATCH_ID = "3.2.2"
DESCRIPTION = "Send email after crypto payment submission."

IMPORT_LINE = "from email_service import send_email"

EMAIL_BLOCK = '''
    try:
        send_email(
            email,
            "Crypto Payment Received - CopySwift AI™",
            f"""
            <h2>Crypto Payment Received</h2>
            <p>Hello,</p>

            <p>We have received your crypto payment submission.</p>

            <ul>
                <li><b>Package:</b> {package}</li>
                <li><b>Coin:</b> {coin}</li>
                <li><b>Transaction Hash:</b> {tx_hash}</li>
                <li><b>Status:</b> Pending Verification</li>
            </ul>

            <p>Our team will verify your transaction shortly.</p>

            <hr>

            <p><b>CopySwift AI™ Team</b></p>
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
        changes.append("Added email import.")

    if EMAIL_BLOCK.strip() not in app_text:
        target = "    session['user_email'] = email"
        replacement = target + "\n" + EMAIL_BLOCK.rstrip()
        app_text = app_text.replace(target, replacement, 1)
        changes.append("Crypto email integrated.")

    return app_text, changes
