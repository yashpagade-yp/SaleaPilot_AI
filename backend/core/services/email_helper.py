"""Async Gmail SMTP helper for transactional email delivery."""

from os import getenv

import aiosmtplib
from dotenv import load_dotenv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from commons.logger import logger

load_dotenv()

logging = logger(__name__)


class EmailDeliveryError(Exception):
    """Raised when transactional email delivery fails."""


async def send_email(subject: str, to_email: str, text: str, html: str) -> bool:
    """Send an email asynchronously via Gmail SMTP using STARTTLS.

    Args:
        subject (str): Email subject line.
        to_email (str): Recipient email address.
        text (str): Plain-text fallback body.
        html (str): HTML body rendered by modern email clients.

    Returns:
        bool: True when email delivery succeeds.

    Raises:
        EmailDeliveryError: If credentials are missing or SMTP handoff fails.
    """
    try:
        logging.info("Executing email_helper.send_email")
        gmail_user = getenv("gmail_user") or getenv("GMAIL")
        gmail_app_password = getenv("gmail_app_password") or getenv("GMAIL_APP_PASSWORD")

        if not gmail_user or not gmail_app_password:
            raise EmailDeliveryError("Gmail credentials not configured in .env")

        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = gmail_user
        message["To"] = to_email
        message.attach(MIMEText(text, "plain"))
        message.attach(MIMEText(html, "html"))

        await aiosmtplib.send(
            message,
            hostname="smtp.gmail.com",
            port=587,
            start_tls=True,
            username=gmail_user,
            password=gmail_app_password,
        )

        logging.info(f"Email sent to {to_email} | subject: {subject}")
        return True
    except EmailDeliveryError:
        raise
    except Exception as error:
        logging.error(f"send_email failed for {to_email}: {error}")
        raise EmailDeliveryError(str(error)) from error
