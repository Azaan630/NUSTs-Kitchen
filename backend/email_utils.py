import os
import smtplib
import logging
import threading
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger(__name__)

SMTP_HOST = os.getenv("SMTP_HOST", "")
try:
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
except (ValueError, TypeError):
    SMTP_PORT = 587
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASS = os.getenv("SMTP_PASS", "")
FROM_EMAIL = os.getenv("FROM_EMAIL", "")

SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY", "")

logger.info("SMTP config: host=%s port=%s user=%s  SendGrid=%s",
            SMTP_HOST or "(unset)", SMTP_PORT, SMTP_USER or "(unset)",
            "set" if SENDGRID_API_KEY else "unset")


def _send_via_sendgrid(to_email, subject, body_text, body_html=None):
    import urllib.request, json
    data = {
        "personalizations": [{"to": [{"email": to_email}]}],
        "from": {"email": FROM_EMAIL or SMTP_USER or "noreply@nustskitchen.com"},
        "subject": subject,
        "content": [{"type": "text/plain", "value": body_text}],
    }
    if body_html:
        data["content"].append({"type": "text/html", "value": body_html})
    req = urllib.request.Request(
        "https://api.sendgrid.com/v3/mail/send",
        data=json.dumps(data).encode(),
        headers={
            "Authorization": f"Bearer {SENDGRID_API_KEY}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    urllib.request.urlopen(req, timeout=10)


def _smtp_send(to_email, msg):
    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, timeout=5) as s:
        s.login(SMTP_USER, SMTP_PASS)
        s.sendmail(FROM_EMAIL or SMTP_USER, to_email, msg.as_string())


def _build_msg(to_email, subject, body_text, body_html=None):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = FROM_EMAIL or SMTP_USER
    msg["To"] = to_email
    msg.attach(MIMEText(body_text, "plain"))
    if body_html:
        msg.attach(MIMEText(body_html, "html"))
    return msg


def _notify_one(to_email, name, amount, due_date, month):
    if (not SMTP_HOST or not SMTP_USER or not SMTP_PASS) and not SENDGRID_API_KEY:
        logger.warning("No email transport configured; skipping %s", to_email)
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
    </div>"""
    try:
        if SENDGRID_API_KEY:
            _send_via_sendgrid(to_email, subject, body_text, body_html)
        else:
            msg = _build_msg(to_email, subject, body_text, body_html)
            _smtp_send(to_email, msg)
        logger.info("Email sent to %s", to_email)
    except Exception as e:
        logger.error("Email to %s failed: %s", to_email, e)


def notify_students(students: list[dict]):
    """Fire off one daemon thread per student to send bill notification.
       Each student dict must have: Email, First_Name, Last_Name, Amount, Due_Date, Month."""
    for s in students:
        threading.Thread(
            target=_notify_one,
            args=(s["Email"],
                  f"{s.get('First_Name','')} {s.get('Last_Name','')}".strip(),
                  s["Amount"], s["Due_Date"], s["Month"]),
            daemon=True,
        ).start()
    logger.info("Dispatched %d email notifications", len(students))
