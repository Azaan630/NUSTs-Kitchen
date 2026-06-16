import os
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger("email")

GMAIL_USER = os.getenv("GMAIL_USER", "zainif63@gmail.com")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD", "")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "zainif63@gmail.com")

if GMAIL_APP_PASSWORD:
    logger.info("Gmail SMTP configured for %s", GMAIL_USER)
else:
    logger.warning("GMAIL_APP_PASSWORD not set — email sending disabled. "
                   "Generate one at: https://myaccount.google.com/apppasswords")


def send_email_sync(to_email: str, subject: str, html_body: str) -> bool:
    if not GMAIL_APP_PASSWORD:
        logger.warning("GMAIL_APP_PASSWORD not set — skipping email to %s", to_email)
        return False
    try:
        msg = MIMEMultipart("alternative")
        msg["From"] = GMAIL_USER
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(html_body, "html"))

        with smtplib.SMTP("smtp.gmail.com", 587, timeout=15) as server:
            server.starttls()
            server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
            server.sendmail(GMAIL_USER, to_email, msg.as_string())

        logger.info("Email sent to %s: %s", to_email, subject)
        return True
    except smtplib.SMTPAuthenticationError:
        logger.error("Gmail auth failed — check GMAIL_APP_PASSWORD. "
                     "Generate at: https://myaccount.google.com/apppasswords")
        return False
    except Exception as e:
        logger.error("Email send failed to %s: %s", to_email, e)
        return False


def registration_requested_email(name: str, email: str) -> tuple:
    subject = "Registration Request Received — NUST Kitchen"
    body = f"""\
<div style="font-family:Arial,sans-serif;max-width:600px;margin:auto;padding:20px">
    <h2 style="color:#1D4ED8">NUST Kitchen</h2>
    <p>Hi <strong>{name}</strong>,</p>
    <p>Your registration request has been <strong>received</strong> and is pending admin approval.</p>
    <p>We'll notify you once it's reviewed. This usually takes 24-48 hours.</p>
    <hr style="border:1px solid #eee">
    <p style="color:#888;font-size:12px">NUST Kitchen — Smart Mess Management for NUST Hostels</p>
</div>"""
    return subject, body


def registration_approved_email(name: str, email: str) -> tuple:
    subject = "Registration Approved — Welcome to NUST Kitchen!"
    body = f"""\
<div style="font-family:Arial,sans-serif;max-width:600px;margin:auto;padding:20px">
    <h2 style="color:#10B981">Welcome to NUST Kitchen!</h2>
    <p>Hi <strong>{name}</strong>,</p>
    <p>Your registration has been <strong>approved</strong>! You can now sign in with your Google account.</p>
    <p>Enjoy smart mess management — menus, billing, voting, and more.</p>
    <hr style="border:1px solid #eee">
    <p style="color:#888;font-size:12px">NUST Kitchen — Smart Mess Management for NUST Hostels</p>
</div>"""
    return subject, body


def account_deleted_email(name: str, email: str) -> tuple:
    subject = "Account Removed — NUST Kitchen"
    body = f"""\
<div style="font-family:Arial,sans-serif;max-width:600px;margin:auto;padding:20px">
    <h2 style="color:#EF4444">Account Removed</h2>
    <p>Hi <strong>{name}</strong>,</p>
    <p>Your account has been <strong>removed</strong> from NUST Kitchen by an administrator.</p>
    <p>If you believe this is a mistake, please contact your hostel administration.</p>
    <hr style="border:1px solid #eee">
    <p style="color:#888;font-size:12px">NUST Kitchen — Smart Mess Management for NUST Hostels</p>
</div>"""
    return subject, body


def bill_issued_email(name: str, email: str, amount: float, month: str, due_date: str) -> tuple:
    subject = f"New Bill Issued — {month} — NUST Kitchen"
    body = f"""\
<div style="font-family:Arial,sans-serif;max-width:600px;margin:auto;padding:20px">
    <h2 style="color:#1D4ED8">Bill Issued</h2>
    <p>Hi <strong>{name}</strong>,</p>
    <p>A new mess bill has been issued for <strong>{month}</strong>:</p>
    <div style="background:#f8fafc;border-radius:8px;padding:16px;margin:16px 0">
        <p style="font-size:24px;font-weight:bold;color:#1D4ED8;margin:0">PKR {amount:,.2f}</p>
        <p style="color:#888;margin:4px 0 0 0">Due by: <strong>{due_date}</strong></p>
    </div>
    <p>Please pay before the due date to avoid overdue charges.</p>
    <hr style="border:1px solid #eee">
    <p style="color:#888;font-size:12px">NUST's Kitchen — Smart Mess Management for NUST Hostels</p>
</div>"""
    return subject, body


def feedback_email(user_name: str, user_email: str, message: str) -> tuple:
    subject = f"Feedback from {user_name} — NUST Kitchen"
    body = f"""\
<div style="font-family:Arial,sans-serif;max-width:600px;margin:auto;padding:20px">
    <h2 style="color:#6366F1">New Feedback</h2>
    <p><strong>From:</strong> {user_name} ({user_email})</p>
    <div style="background:#f8fafc;border-radius:8px;padding:16px;margin:16px 0;border-left:4px solid #6366F1">
        <p style="margin:0;white-space:pre-wrap">{message}</p>
    </div>
    <hr style="border:1px solid #eee">
    <p style="color:#888;font-size:12px">NUST Kitchen — Feedback System</p>
</div>"""
    return subject, body
