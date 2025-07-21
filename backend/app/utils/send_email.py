import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv
import aiosmtplib

load_dotenv()

SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")
SENDER_NAME = os.getenv("EMAIL_SENDER_NAME")


async def send_reset_email(to_email: str, reset_link: str):
    subject = "Password Reset Request"
    sender = f"{SENDER_NAME} <{SMTP_USER}>"
    recipient = to_email

    text = f"""\
Hi,

You requested a password reset. Click the link below to reset your password:

{reset_link}

If you did not make this request, please ignore this email.
"""
    html = f"""\
<html>
  <body>
    <p>Hi,<br><br>
       You requested a password reset. Click the button below to reset your password:<br><br>
       <a href="{reset_link}" style="padding: 10px 20px; background-color: #007BFF; color: white; text-decoration: none;">Reset Password</a><br><br>
       If you did not make this request, please ignore this email.
    </p>
  </body>
</html>
"""

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = recipient

    msg.attach(MIMEText(text, "plain"))
    msg.attach(MIMEText(html, "html"))

    try:
        await aiosmtplib.send(
            msg,
            hostname=SMTP_HOST,
            port=SMTP_PORT,
            start_tls=True,
            username=SMTP_USER,
            password=SMTP_PASS,
        )
        print(f"Email sent to {recipient}")
    except Exception as e:
        print(f"Failed to send email: {e}")
        raise e
