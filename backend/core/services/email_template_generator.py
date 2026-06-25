"""HTML and plain-text email template builders for SalesPilot AI."""

from os import getenv


def _company_name() -> str:
    """Return the configured company display name.

    Returns:
        str: Company or product brand shown in email content.
    """
    return getenv("company_name") or getenv("COMPANY_NAME") or "SalesPilot AI"


def _support_email() -> str:
    """Return the configured support email address.

    Returns:
        str: Support mailbox shown in email footer content.
    """
    return (
        getenv("support_email")
        or getenv("SUPPORT_EMAIL")
        or getenv("gmail_user")
        or getenv("GMAIL")
        or "support@example.com"
    )


def _logo_url() -> str:
    """Return the configured logo URL for email branding.

    Returns:
        str: Absolute logo URL or an empty string when unavailable.
    """
    return getenv("logo_url") or getenv("LOGO_URL") or ""


def _base_html(title: str, body_html: str) -> str:
    """Wrap body content inside a responsive HTML email shell.

    Args:
        title (str): HTML document title.
        body_html (str): Inner HTML fragment for the email body.

    Returns:
        str: Complete HTML email document.
    """
    company_name = _company_name()
    support_email = _support_email()
    logo_url = _logo_url()

    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>{title}</title>
</head>
<body style="margin:0;padding:0;background:#f4f4f4;font-family:Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#f4f4f4;padding:40px 0;">
    <tr>
      <td align="center">
        <table width="600" cellpadding="0" cellspacing="0"
               style="background:#ffffff;border-radius:8px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,.1);">
          <tr>
            <td style="background:#000000;padding:24px;text-align:center;">
              {"<img src='" + logo_url + "' alt='" + company_name + "' height='40'/>" if logo_url else f"<span style='color:#fff;font-size:22px;font-weight:bold;'>{company_name}</span>"}
            </td>
          </tr>
          <tr>
            <td style="padding:40px 48px;">
              {body_html}
            </td>
          </tr>
          <tr>
            <td style="background:#f9f9f9;padding:20px 48px;text-align:center;color:#999;font-size:12px;border-top:1px solid #eee;">
              Need help? Email us at
              <a href="mailto:{support_email}" style="color:#000;">{support_email}</a><br/>
              &copy; {company_name}. All rights reserved.
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>
"""


def generate_email_template(
    *,
    name: str,
    subject: str,
    title: str,
    description: str,
    action_code: str = "",
    cta_text: str = "",
    cta_link: str = "",
    footer_note: str = "",
) -> dict[str, str]:
    """Build a branded email with optional code and CTA button.

    Args:
        name (str): Recipient display name.
        subject (str): Email subject line.
        title (str): Primary heading shown in the email body.
        description (str): Main body description text.
        action_code (str): Optional invitation token or OTP value.
        cta_text (str): Optional button label.
        cta_link (str): Optional button URL.
        footer_note (str): Optional note shown below the main message.

    Returns:
        dict[str, str]: Subject plus plain-text and HTML bodies.
    """
    code_block = ""
    if action_code:
        code_block = f"""
          <div style="text-align:center;margin:28px 0;">
            <span style="display:inline-block;background:#000;color:#fff;font-size:28px;font-weight:bold;letter-spacing:4px;padding:16px 28px;border-radius:6px;">
              {action_code}
            </span>
          </div>
        """

    cta_block = ""
    if cta_text and cta_link:
        cta_block = f"""
          <div style="text-align:center;margin:28px 0;">
            <a href="{cta_link}"
               style="display:inline-block;background:#000;color:#fff;padding:14px 32px;border-radius:6px;text-decoration:none;font-size:15px;font-weight:bold;">
              {cta_text}
            </a>
          </div>
        """

    footer_note_block = ""
    if footer_note:
        footer_note_block = (
            f'<p style="color:#666;font-size:13px;line-height:1.6;margin-top:24px;">{footer_note}</p>'
        )

    body_html = f"""
      <h2 style="color:#000;margin-bottom:8px;">{title}</h2>
      <p style="color:#555;font-size:15px;line-height:1.6;">Hi {name},</p>
      <p style="color:#444;font-size:15px;line-height:1.6;">{description}</p>
      {code_block}
      {cta_block}
      {footer_note_block}
    """

    text = f"{title}\n\nHi {name},\n\n{description}"
    if action_code:
        text += f"\n\nCode: {action_code}"
    if cta_text and cta_link:
        text += f"\n\n{cta_text}: {cta_link}"
    if footer_note:
        text += f"\n\n{footer_note}"

    return {"subject": subject, "text": text, "html": _base_html(subject, body_html)}


def build_salesperson_invitation_email(
    *,
    name: str,
    invitation_token: str,
    accept_invitation_url: str,
) -> dict[str, str]:
    """Build the salesperson invitation email payload.

    Args:
        name (str): Recipient display name.
        invitation_token (str): Invitation code fallback value.
        accept_invitation_url (str): Invitation acceptance link.

    Returns:
        dict[str, str]: Subject plus plain-text and HTML bodies.
    """
    return generate_email_template(
        name=name,
        subject=f"{_company_name()} Invitation",
        title="You are invited to SalesPilot AI",
        description=(
            f"You have been invited to {_company_name()} as a salesperson. "
            "Use the secure link below to continue, or use the invitation code "
            "if you need to paste it manually."
        ),
        action_code=invitation_token,
        cta_text="Accept invitation",
        cta_link=accept_invitation_url,
        footer_note=(
            "Next steps: open the invitation link, confirm your invited email, "
            "request your email OTP, and complete your profile."
        ),
    )


def build_salesperson_otp_email(*, name: str, otp: str) -> dict[str, str]:
    """Build the salesperson OTP email payload.

    Args:
        name (str): Recipient display name.
        otp (str): One-time password sent to the invited email.

    Returns:
        dict[str, str]: Subject plus plain-text and HTML bodies.
    """
    return generate_email_template(
        name=name,
        subject=f"{_company_name()} Login OTP",
        title="Your SalesPilot AI OTP",
        description=(
            "Use this one-time password to continue your secure salesperson "
            "login. This OTP expires in 10 minutes."
        ),
        action_code=otp,
        footer_note="If you did not request this OTP, you can safely ignore this email.",
    )
