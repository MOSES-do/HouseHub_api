#!/usr/bin/python3

from flask_mail import Message
from flask import url_for, current_app
from .services.jwt_service import create_jwt_token_verify_email
from .config import Config
import os



# Send verification email
def send_verification_email(mail, user):
    sender = current_app.config.get('MAIL_DEFAULT_SENDER')
    token = create_jwt_token_verify_email(user.id, Config.JWT_SECRET_KEY)
    #verification_url = url_for('app_views.verify_email', token=token, _external=True)
    verification_url = f"https://aceme.tech{url_for('app_views.verify_email', token=token)}"

    msg = Message(
            subject="Verify Your Email",
                sender=sender,
                recipients=[user.email],
                body= f"Click the link to verify your email: {verification_url}"
        )

    try:
        mail.send(msg)
    except smtplib.SMTPConnectError as connect_error:
        print(f"SMTP Connection Error: {connect_error}")
    except smtplib.SMTPException as smtp_error:
        print(f"SMTP Error: {smtp_error}")
    except Exception as e:
        print(f"General Error: {e}")


# Send password reset email
def send_password_reset_email(mail, user):
    sender = current_app.config.get('MAIL_DEFAULT_SENDER')
    token = create_jwt_token_verify_email(user.id, Config.JWT_SECRET_KEY, expires_in=Config.PASSWORD_RESET_EXPIRY)
    print(user.email)
    #reset_url = url_for('app_views.reset-password', token=token, _external=True)
    reset_url = f"https://aceme.tech{url_for('app_views.reset_password', token=token)}"

    msg = Message(
            subject="Reset Your Password",
                sender=sender,
                recipients=[user.email],
                body= f"Click the link to reset your password: {reset_url}"
        )

    try:
        mail.send(msg)
    except smtplib.SMTPConnectError as connect_error:
        print(f"SMTP Connection Error: {connect_error}")
    except smtplib.SMTPException as smtp_error:
        print(f"SMTP Error: {smtp_error}")
    except Exception as e:
        print(f"General Error: {e}")
