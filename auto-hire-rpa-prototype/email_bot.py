import smtplib
from email.message import EmailMessage
from config import Config

def send_interview_email(to_email, subject, body):
    try:
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = Config.EMAIL_FROM
        msg["To"] = to_email
        msg.set_content(body)

        server = smtplib.SMTP(Config.SMTP_HOST, Config.SMTP_PORT, timeout=10)
        server.starttls()
        server.login(Config.SMTP_USER, Config.SMTP_PASS)
        server.send_message(msg)
        server.quit()
        return True, None
    except Exception as e:
        return False, e
