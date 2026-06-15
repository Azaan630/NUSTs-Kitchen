import os
import smtplib
import logging
import threading
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger(__name__)

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
try:
    SMTP_PORT = int(os.getenv("SMTP_PORT", "465"))
except (ValueError, TypeError):
    SMTP_PORT = 465
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASS = os.getenv("SMTP_PASS", "")
FROM_EMAIL = os.getenv("FROM_EMAIL", "")

logger.info("SMTP: host=%s port=%s user=%s", SMTP_HOST, SMTP_PORT, SMTP_USER or "(unset)")


def _notify_one(to_email, name, amount, due_date, month):
    if not SMTP_USER or not SMTP_PASS:
        logger.warning("SMTP_USER/PASS not set; skipping %s", to_email)
        return
    subject = f"Bill Issued – NUST's Kitchen ({month})"
    body_text = (
        f"Dear {name},\n\n"
        f"A new mess bill has been issued for {month}.\n"
        f"Amount: Rs. {amount:,.2f}\n"
        f"Due Date: {due_date}\n\n"
        f"Please log in to the portal to view and pay your bill.\n\n"
        f"Regards,\nNUST's Kitchen"
    )
    body_html = f"""\
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
</div>"""
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = FROM_EMAIL or SMTP_USER
        msg["To"] = to_email
        msg.attach(MIMEText(body_text, "plain"))
        msg.attach(MIMEText(body_html, "html"))
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, timeout=10) as s:
            s.login(SMTP_USER, SMTP_PASS)
            s.sendmail(FROM_EMAIL or SMTP_USER, to_email, msg.as_string())
            logger.info("Email sent to %s", to_email)
    except Exception as e:
        logger.error("Email to %s failed: %s", to_email, e)


def notify_students(students: list[dict]):
    if not SMTP_USER or not SMTP_PASS:
        logger.warning("SMTP not configured — set SMTP_USER + SMTP_PASS env vars")
        return
    for s in students:
        threading.Thread(
            target=_notify_one,
            args=(s["Email"],
                  f"{s.get('First_Name','')} {s.get('Last_Name','')}".strip(),
                  s["Amount"], s["Due_Date"], s["Month"]),
            daemon=True,
        ).start()
    logger.info("Dispatched %d email notifications", len(students))
