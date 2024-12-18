#!/usr/bin/python3

from flask_mail import Message
from flask import url_for, current_app
from .services.jwt_service import create_jwt_token_verify_email
from .config import Config
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os


# Email details
sender_email = os.getenv('MAIL_USERNAME')
sender_password = os.getenv('MAIL_PASSWORD')
smtp_server = os.getenv('MAIL_SERVER')
smtp_port = os.getenv('MAIL_PORT')
msg = MIMEMultipart()
msg["From"] = sender_email

# Send verification email
def send_verification_email(mail, user):
    msg["To"] = user.email
    print(user.email)
    msg["Subject"] = "Verify Your Email"
    token = create_jwt_token_verify_email(user.id, Config.JWT_SECRET_KEY)
    verification_url = url_for('app_views.verify_email', token=token, _external=True)
    body=f"Click the link to verify your email: {verification_url}"
    msg.attach(MIMEText(body, "plain"))
    try:
    # Using 'with' to automatically handle the connection and disconnection
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.connect(smtp_server, smtp_port)
            server.starttls()  # Secure the connection
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, user.email, msg.as_string())
            print("Email sent successfully!")
            print(token)
    except Exception as e:
        print(f"Error: {e}")

# Send password reset email
def send_password_reset_email(mail, user):
    msg["To"] = user.email
    msg["Subject"] = "Reset Your Password"
    token = create_jwt_token_verify_email(user.id, Config.JWT_SECRET_KEY, expires_in=Config.PASSWORD_RESET_EXPIRY)
    reset_url = url_for('app_views.verify_email', token=token, _external=True)
    msg.attach(MIMEText(body, "plain"))
     
    try:
    # Using 'with' to automatically handle the connection and disconnection
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # Secure the connection
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, user.email, msg.as_string())
            print("Email sent successfully!")
    except Exception as e:
        print(f"Error: {e}")
