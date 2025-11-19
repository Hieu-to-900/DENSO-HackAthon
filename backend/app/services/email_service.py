# app/core/email.py
import os
from mailtrap import MailtrapClient, Mail, Address

MAILTRAP_TOKEN = "f6c30d76c8dd08d26b8fa741afd93470"
SENDER_EMAIL = "phuoc.dang2104@gmail.com"
SENDER_NAME = "DENSO ADMIN"

# Tạo client 1 lần
client = MailtrapClient(token=MAILTRAP_TOKEN)


def send_assignment_email(to_email: str, subject: str, body_html: str):
    if not MAILTRAP_TOKEN:
        raise RuntimeError("MAILTRAP_API_TOKEN is not set")

    mail = Mail(
        sender=Address(email=SENDER_EMAIL, name=SENDER_NAME),
        to=[Address(email=to_email)],
        subject=subject,
        html=body_html,        # dùng HTML
        category="Assignment", # tag cho dễ lọc
    )

    resp = client.send(mail)
    print("[Mailtrap] Response:", resp)
    return resp
