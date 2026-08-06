"""
============================================================
CopySwift AI Notification Center
Email Notifications
============================================================
"""

try:
    from email_service import send_email
except ImportError:
    send_email = None


def send_notification_email(
    to_email,
    subject,
    html,
    text=None
):
    """
    Send a notification email using the configured email service.
    """

    if send_email is None:
        raise RuntimeError("email_service.send_email() not available.")

    return send_email(
        to_email=to_email,
        subject=subject,
        html=html,
        text=text,
    )
