import os
import httpx
import logging

logger = logging.getLogger("email")

RESEND_API_KEY = os.getenv("RESEND_API_KEY", "")
RESEND_FROM = "NUST Kitchen <noreply@kitchen.resend.dev>"


async def send_email(to_email: str, subject: str, html_body: str) -> bool:
    if not RESEND_API_KEY:
        logger.warning("RESEND_API_KEY not set — skipping email to %s", to_email)
        return False
    try:
        async with httpx.AsyncClient() as client:
            r = await client.post(
                "https://api.resend.com/emails",
                headers={
                    "Authorization": f"Bearer {RESEND_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "from": RESEND_FROM,
                    "to": [to_email],
                    "subject": subject,
                    "html": html_body,
                },
                timeout=15.0,
            )
            if r.status_code in (200, 201):
                logger.info("Email sent to %s: %s", to_email, subject)
                return True
            logger.error("Resend API error %s: %s", r.status_code, r.text)
            return False
    except Exception as e:
        logger.error("Email send failed: %s", e)
        return False


def registration_requested_email(name: str, email: str) -> tuple:
    subject = "Registration Request Received — NUST Kitchen"
    body = f"""
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
    body = f"""
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
    body = f"""
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
    body = f"""
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
        <p style="color:#888;font-size:12px">NUST Kitchen — Smart Mess Management for NUST Hostels</p>
    </div>"""
    return subject, body
