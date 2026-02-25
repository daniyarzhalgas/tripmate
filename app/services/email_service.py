import asyncio
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Iterable, Optional

from app.core.config import config


def _build_message(
    subject: str,
    body: str,
    to_emails: Iterable[str],
    from_email: Optional[str] = None,
) -> MIMEMultipart:
    message = MIMEMultipart()
    message["From"] = from_email or config.SMTP_FROM_EMAIL
    message["To"] = ", ".join(to_emails)
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))
    return message


def _send_email_sync(message: MIMEMultipart) -> None:
    if not config.EMAIL_ENABLED:
        print("EMAIL_DISABLED:", message.as_string())
        return

    with smtplib.SMTP(config.SMTP_HOST, config.SMTP_PORT) as server:
        if config.SMTP_USE_TLS:
            server.starttls()
        if config.SMTP_USERNAME and config.SMTP_PASSWORD:
            server.login(config.SMTP_USERNAME, config.SMTP_PASSWORD)
        server.send_message(message)


async def send_email(
    subject: str,
    body: str,
    to_emails: Iterable[str],
    from_email: Optional[str] = None,
) -> None:
    message = _build_message(subject=subject, body=body, to_emails=to_emails, from_email=from_email)
    await asyncio.to_thread(_send_email_sync, message)


async def send_verification_email(email: str, code: str) -> None:
    subject = "Verify your Tripmate email"
    body = (
        "Welcome to Tripmate!\n\n"
        f"Your verification code is: {code}\n\n"
        "If you did not request this, you can ignore this email."
    )
    await send_email(subject=subject, body=body, to_emails=[email])


async def send_welcome_email(email: str, first_name: str) -> None:
    subject = "Welcome to Tripmate 🎉"
    body = (
        f"Hi {first_name},\n\n"
        "Thanks for signing up for Tripmate. We're excited to have you on board!\n\n"
        "Happy travels,\n"
        "The Tripmate Team"
    )
    await send_email(subject=subject, body=body, to_emails=[email])


async def send_password_reset_email(email: str, token: str) -> None:
    subject = "Reset your Tripmate password"
    if config.FRONTEND_RESET_PASSWORD_URL:
        reset_link = f"{config.FRONTEND_RESET_PASSWORD_URL}?token={token}"
        body = (
            "We received a request to reset your Tripmate password.\n\n"
            f"You can reset your password by visiting this link:\n{reset_link}\n\n"
            "If you did not request a password reset, you can safely ignore this email."
        )
    else:
        body = (
            "We received a request to reset your Tripmate password.\n\n"
            f"Use this token to reset your password: {token}\n\n"
            "If you did not request a password reset, you can safely ignore this email."
        )
    await send_email(subject=subject, body=body, to_emails=[email])

