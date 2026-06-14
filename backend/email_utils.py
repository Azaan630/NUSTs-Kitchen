import os
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger(__name__)

SMTP_HOST = os.getenv("SMTP_HOST", "")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASS = os.getenv("SMTP_PASS", "")
FROM_EMAIL = os.getenv("FROM_EMAIL", "noreply@nustskitchen.app")


def send_email(to_email: str, subject: str, body_text: str, body_html: str = None):
    if not SMTP_HOST or not SMTP_USER or not SMTP_PASS:
        logger.warning("SMTP not configured; skipping email to %s", to_email)
        return
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = FROM_EMAIL
    msg["To"] = to_email
    msg.attach(MIMEText(body_text, "plain"))
    if body_html:
        msg.attach(MIMEText(body_html, "html"))
    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(FROM_EMAIL, to_email, msg.as_string())
        logger.info("Email sent to %s", to_email)
    except Exception as e:
        logger.error("Failed to send email to %s: %s", to_email, e)


def send_bill_notification(to_email: str, name: str, amount: float, due_date: str, month: str):
    subject = f"Bill Issued – NUST's Kitchen ({month})"
    body_text = (
        f"Dear {name},\n\n"
        f"A new mess bill has been issued for {month}.\n"
        f"Amount: Rs. {amount:,.2f}\n"
        f"Due Date: {due_date}\n\n"
        f"Please log in to the portal to view and pay your bill.\n\n"
        f"Regards,\nNUST's Kitchen"
    )
    body_html = f"""
    <div style="font-family:sans-serif;max-width:480px;margin:0 auto;">
      <h2 style="color:#1D4ED8;">NUST&rsquo;s Kitchen</h2>
      <p>Dear {name},</p>
      <p>A new mess bill has been issued:</p>
      <table style="border-collapse:collapse;width:100%">
        <tr><td style="padding:6px 0;color:#666;">Month</td>
            <td style="padding:6px 0;font-weight:bold;">{month}</td></tr>
        <tr><td style="padding:6px 0;color:#666;">Amount</td>
            <td style="padding:6px 0;font-weight:bold;">Rs. {amount:,.2f}</td></tr>
        <tr><td style="padding:6px 0;color:#666;">Due Date</td>
            <td style="padding:6px 0;font-weight:bold;">{due_date}</td></tr>
      </table>
      <p>Please log in to the portal to view and pay your bill.</p>
      <hr style="border:none;border-top:1px solid #eee;">
      <p style="color:#999;font-size:12px;">NUST&rsquo;s Kitchen &middot; Mess Management System</p>
    </div>
    """
    send_email(to_email, subject, body_text, body_html)
