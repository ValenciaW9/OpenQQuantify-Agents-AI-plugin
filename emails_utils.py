import smtplib
from email.mime.text import MIMEText
import os 

def send_email(subject, recipient, body):
    sender_email = os.getenv("SENDER_EMAIL")
    sender_password = os.getenv("SENDER_APP_PASSWORD") # Get from environment variable

    if not sender_email or not sender_password:
        print("Email sender credentials not set in environment variables. Email not sent.")
        return False

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = recipient

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_password)
            server.send_message(msg)
        print(f"Email sent successfully to {recipient} with subject: {subject}")
        return True
    except Exception as e:
        print(f"Failed to send email to {recipient}: {e}")
        return False