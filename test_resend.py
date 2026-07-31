from email_service import send_email

recipient = "anthutuyello@gmail.com"

ok = send_email(
    recipient,
    "🎉 CopySwift AI™ Resend Test",
    """
    <h2>Congratulations!</h2>
    <p>This is the first live email sent from <b>CopySwift AI™</b> using Resend.</p>
    <p>If you received this email, your email integration is working correctly.</p>
    <hr>
    <p>CopySwift AI™ Notification Framework v3.2</p>
    """
)

if ok:
    print("SUCCESS: Email sent.")
else:
    print("FAILED: Email was not sent.")
