"""Service layer for sending transactional emails through Gmail SMTP."""

import smtplib
from email.message import EmailMessage

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from commons.logger import logger

load_dotenv()

logging = logger(__name__)


class EmailSettings(BaseSettings):
    """Environment-backed Gmail SMTP settings."""

    gmail: str = Field(..., alias="GMAIL")
    gmail_app_password: str = Field(..., alias="GMAIL_APP_PASSWORD")

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        populate_by_name=True,
    )


class EmailService:
    """Service facade for transactional Gmail email delivery."""

    def __init__(self) -> None:
        """Initialize Gmail SMTP configuration."""
        logging.info("Executing EmailService.__init__")
        self.settings = EmailSettings()

    def send_email(
        self,
        *,
        to_email: str,
        subject: str,
        body: str,
    ) -> None:
        """Send a plain-text email through Gmail SMTP.

        Args:
            to_email (str): Recipient email address.
            subject (str): Email subject line.
            body (str): Plain-text email body.

        Raises:
            Exception: If SMTP authentication or delivery fails.
        """
        try:
            logging.info("Executing EmailService.send_email")
            message = EmailMessage()
            message["From"] = self.settings.gmail
            message["To"] = to_email
            message["Subject"] = subject
            message.set_content(body)

            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp_server:
                smtp_server.login(
                    self.settings.gmail,
                    self.settings.gmail_app_password,
                )
                smtp_server.send_message(message)

            logging.info(f"Email sent successfully to {to_email}")
        except Exception as error:
            logging.error(f"Error in EmailService.send_email: {error}")
            raise error
