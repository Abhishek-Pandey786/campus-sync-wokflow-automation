"""
Email Notification Service (Option A)
Sends email alerts for high-risk requests via SMTP.
Falls back to console logging when SMTP is not configured.
"""

import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
from typing import Optional

from core.config import settings

logger = logging.getLogger(__name__)


def _send_smtp(subject: str, html_body: str, to_email: str) -> bool:
    """
    Send an email via SMTP.
    Returns True on success, False on failure.
    """
    if not settings.EMAIL_ENABLED or not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        logger.info(f"[EMAIL-MOCK] To={to_email} | Subject={subject}")
        return False

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = settings.SMTP_USER
        msg["To"] = to_email
        msg.attach(MIMEText(html_body, "html"))

        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10) as server:
            server.ehlo()
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(settings.SMTP_USER, to_email, msg.as_string())

        logger.info(f"[EMAIL-SENT] To={to_email} | Subject={subject}")
        return True

    except Exception as exc:
        logger.error(f"[EMAIL-ERROR] {exc}")
        return False


def _get_urgency_badge(urgency: str) -> str:
    colours = {
        "critical": "#dc2626",
        "high":     "#ea580c",
        "medium":   "#ca8a04",
        "low":      "#16a34a",
    }
    colour = colours.get(urgency, "#6b7280")
    return (
        f'<span style="background:{colour};color:white;padding:2px 8px;'
        f'border-radius:4px;font-size:12px;font-weight:bold;">'
        f'{urgency.upper()}</span>'
    )


def notify_high_risk_request(
    request_id: int,
    request_number: str,
    request_type: str,
    student_name: str,
    risk_score: float,
    urgency: str,
    hours_remaining: Optional[float],
    to_email: Optional[str] = None,
) -> bool:
    """
    Send a high-risk delay alert for a service request.
    Uses NOTIFY_ADMIN_EMAIL if to_email is not provided.
    """
    recipient = to_email or settings.NOTIFY_ADMIN_EMAIL or settings.ADMIN_EMAIL
    subject = f"⚠️ Delay Alert [{urgency.upper()}]: {request_number} – {request_type.replace('_', ' ').title()}"

    hours_label = (
        f"{hours_remaining:.1f} hours remaining"
        if hours_remaining is not None and hours_remaining > 0
        else "SLA already breached"
    )

    html = f"""
    <html><body style="font-family:Arial,sans-serif;background:#f3f4f6;padding:24px;">
      <div style="max-width:600px;margin:0 auto;background:white;border-radius:8px;
                  box-shadow:0 2px 8px rgba(0,0,0,.1);overflow:hidden;">
        <div style="background:#1e293b;padding:20px 24px;">
          <h2 style="margin:0;color:white;">⚠️ Workflow Delay Alert</h2>
          <p style="margin:4px 0 0;color:#94a3b8;font-size:13px;">
            {datetime.now().strftime('%Y-%m-%d %H:%M')}
          </p>
        </div>
        <div style="padding:24px;">
          <p>A service request has been flagged as high-risk for delay.</p>
          <table style="width:100%;border-collapse:collapse;margin:16px 0;">
            <tr><td style="padding:8px 12px;background:#f8fafc;font-weight:bold;width:40%;">Request Number</td>
                <td style="padding:8px 12px;">{request_number}</td></tr>
            <tr><td style="padding:8px 12px;background:#f8fafc;font-weight:bold;">Request Type</td>
                <td style="padding:8px 12px;">{request_type.replace('_', ' ').title()}</td></tr>
            <tr><td style="padding:8px 12px;background:#f8fafc;font-weight:bold;">Student</td>
                <td style="padding:8px 12px;">{student_name}</td></tr>
            <tr><td style="padding:8px 12px;background:#f8fafc;font-weight:bold;">Risk Score</td>
                <td style="padding:8px 12px;"><strong>{risk_score*100:.1f}%</strong></td></tr>
            <tr><td style="padding:8px 12px;background:#f8fafc;font-weight:bold;">Urgency</td>
                <td style="padding:8px 12px;">{_get_urgency_badge(urgency)}</td></tr>
            <tr><td style="padding:8px 12px;background:#f8fafc;font-weight:bold;">SLA Status</td>
                <td style="padding:8px 12px;">{hours_label}</td></tr>
          </table>
          <p style="color:#6b7280;font-size:13px;">
            Please review this request in the admin dashboard and take appropriate action.
          </p>
          <a href="http://localhost:5173/alerts"
             style="display:inline-block;background:#2563eb;color:white;padding:10px 20px;
                    border-radius:6px;text-decoration:none;font-weight:bold;">
            View in Dashboard →
          </a>
        </div>
      </div>
    </body></html>
    """

    sent = _send_smtp(subject, html, recipient)
    if not sent:
        logger.warning(
            f"[ALERT] High-risk request {request_number} | "
            f"Student={student_name} | Score={risk_score:.2f} | "
            f"Urgency={urgency} | {hours_label}"
        )
    return sent


def notify_escalation(
    request_id: int,
    request_number: str,
    request_type: str,
    escalated_by: str,
    notes: str = "",
    to_email: Optional[str] = None,
) -> bool:
    """
    Notify admin that a request has been manually escalated.
    """
    recipient = to_email or settings.NOTIFY_ADMIN_EMAIL or settings.ADMIN_EMAIL
    subject = f"🚨 Escalated: {request_number} – {request_type.replace('_', ' ').title()}"

    html = f"""
    <html><body style="font-family:Arial,sans-serif;background:#f3f4f6;padding:24px;">
      <div style="max-width:600px;margin:0 auto;background:white;border-radius:8px;
                  box-shadow:0 2px 8px rgba(0,0,0,.1);overflow:hidden;">
        <div style="background:#7c3aed;padding:20px 24px;">
          <h2 style="margin:0;color:white;">🚨 Request Escalated</h2>
          <p style="margin:4px 0 0;color:#ddd6fe;font-size:13px;">
            {datetime.now().strftime('%Y-%m-%d %H:%M')}
          </p>
        </div>
        <div style="padding:24px;">
          <table style="width:100%;border-collapse:collapse;margin:16px 0;">
            <tr><td style="padding:8px 12px;background:#f8fafc;font-weight:bold;width:40%;">Request Number</td>
                <td style="padding:8px 12px;">{request_number}</td></tr>
            <tr><td style="padding:8px 12px;background:#f8fafc;font-weight:bold;">Request Type</td>
                <td style="padding:8px 12px;">{request_type.replace('_', ' ').title()}</td></tr>
            <tr><td style="padding:8px 12px;background:#f8fafc;font-weight:bold;">Escalated By</td>
                <td style="padding:8px 12px;">{escalated_by}</td></tr>
            <tr><td style="padding:8px 12px;background:#f8fafc;font-weight:bold;">Notes</td>
                <td style="padding:8px 12px;">{notes or '—'}</td></tr>
          </table>
          <a href="http://localhost:5173/alerts"
             style="display:inline-block;background:#7c3aed;color:white;padding:10px 20px;
                    border-radius:6px;text-decoration:none;font-weight:bold;">
            View in Dashboard →
          </a>
        </div>
      </div>
    </body></html>
    """

    sent = _send_smtp(subject, html, recipient)
    if not sent:
        logger.warning(
            f"[ESCALATION] Request {request_number} escalated by {escalated_by}. Notes: {notes}"
        )
    return sent
