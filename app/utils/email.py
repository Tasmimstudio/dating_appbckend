# app/utils/email.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from typing import Optional
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Email Configuration
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")  # Your Gmail address
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")  # Your Gmail App Password
FROM_EMAIL = os.getenv("FROM_EMAIL", SMTP_USERNAME)
FROM_NAME = os.getenv("FROM_NAME", "Dating App")

def send_email(to_email: str, subject: str, html_content: str, text_content: Optional[str] = None) -> bool:
    """
    Send an email using SMTP

    Args:
        to_email: Recipient email address
        subject: Email subject
        html_content: HTML content of the email
        text_content: Plain text content (optional, will use html if not provided)

    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        # Create message
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = f"{FROM_NAME} <{FROM_EMAIL}>"
        message["To"] = to_email

        # Add plain text version
        if text_content:
            text_part = MIMEText(text_content, "plain")
            message.attach(text_part)

        # Add HTML version
        html_part = MIMEText(html_content, "html")
        message.attach(html_part)

        # Connect to SMTP server and send
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()  # Secure the connection
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(message)

        print(f"[SUCCESS] Email sent successfully to {to_email}")
        return True

    except Exception as e:
        print(f"[ERROR] Failed to send email to {to_email}: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def send_password_reset_email(to_email: str, reset_code: str, user_name: str = "User") -> bool:
    """
    Send password reset email with reset code

    Args:
        to_email: User's email address
        reset_code: 6-digit reset code
        user_name: User's name (optional)

    Returns:
        bool: True if email sent successfully
    """
    subject = "Password Reset Request - Dating App"

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #FFD2DA 0%, #C2C3EF 100%);
                margin: 0;
                padding: 20px;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                background: white;
                border-radius: 20px;
                padding: 40px;
                box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            }}
            .header {{
                text-align: center;
                margin-bottom: 30px;
            }}
            .logo {{
                font-size: 48px;
                margin-bottom: 10px;
            }}
            h1 {{
                color: #FFD2DA;
                margin: 0;
                font-size: 28px;
            }}
            .content {{
                color: #333;
                line-height: 1.6;
                font-size: 16px;
            }}
            .code-box {{
                background: linear-gradient(135deg, #FFD2DA 0%, #C2C3EF 100%);
                color: #2B2B2B;
                padding: 20px;
                border-radius: 15px;
                text-align: center;
                margin: 30px 0;
            }}
            .code {{
                font-size: 36px;
                font-weight: bold;
                letter-spacing: 8px;
                font-family: 'Courier New', monospace;
            }}
            .expiry {{
                color: #666;
                font-size: 14px;
                margin-top: 20px;
            }}
            .footer {{
                text-align: center;
                margin-top: 30px;
                padding-top: 20px;
                border-top: 2px solid #f0f0f0;
                color: #666;
                font-size: 14px;
            }}
            .warning {{
                background: #fff3cd;
                border: 2px solid #ffc107;
                border-radius: 10px;
                padding: 15px;
                margin-top: 20px;
                color: #856404;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="logo">Love</div>
                <h1>Password Reset Request</h1>
            </div>

            <div class="content">
                <p>Hi {user_name},</p>

                <p>We received a request to reset your password for your Dating App account. Use the code below to reset your password:</p>

                <div class="code-box">
                    <div class="code">{reset_code}</div>
                </div>

                <p>Enter this code on the password reset page to create a new password.</p>

                <p class="expiry">⏰ This code will expire in <strong>30 minutes</strong>.</p>

                <div class="warning">
                    <strong>Warning Security Notice:</strong> If you didn't request this password reset, please ignore this email. Your account is still secure.
                </div>
            </div>

            <div class="footer">
                <p>Best regards,<br>The Dating App Team</p>
                <p style="font-size: 12px; color: #999;">This is an automated message, please do not reply to this email.</p>
            </div>
        </div>
    </body>
    </html>
    """

    text_content = f"""
    Password Reset Request

    Hi {user_name},

    We received a request to reset your password for your Dating App account.

    Your password reset code is: {reset_code}

    This code will expire in 30 minutes.

    If you didn't request this password reset, please ignore this email.

    Best regards,
    The Dating App Team
    """

    return send_email(to_email, subject, html_content, text_content)


def send_welcome_email(to_email: str, user_name: str) -> bool:
    """
    Send welcome email to new users

    Args:
        to_email: User's email address
        user_name: User's name

    Returns:
        bool: True if email sent successfully
    """
    subject = f"Welcome to Dating App, {user_name}! Welcome"

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #FFD2DA 0%, #C2C3EF 100%);
                margin: 0;
                padding: 20px;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                background: white;
                border-radius: 20px;
                padding: 40px;
                box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            }}
            .header {{
                text-align: center;
                margin-bottom: 30px;
            }}
            .logo {{
                font-size: 64px;
                margin-bottom: 10px;
            }}
            h1 {{
                color: #FFD2DA;
                margin: 0;
                font-size: 32px;
            }}
            .content {{
                color: #333;
                line-height: 1.8;
                font-size: 16px;
            }}
            .cta-button {{
                display: inline-block;
                background: linear-gradient(135deg, #FFD2DA 0%, #C2C3EF 100%);
                color: #2B2B2B;
                padding: 15px 40px;
                border-radius: 25px;
                text-decoration: none;
                font-weight: bold;
                margin: 20px 0;
            }}
            .features {{
                margin: 30px 0;
            }}
            .feature {{
                margin: 15px 0;
                padding: 15px;
                background: #f8f9fa;
                border-radius: 10px;
            }}
            .footer {{
                text-align: center;
                margin-top: 30px;
                padding-top: 20px;
                border-top: 2px solid #f0f0f0;
                color: #666;
                font-size: 14px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="logo">❤️</div>
                <h1>Welcome to Dating App!</h1>
            </div>

            <div class="content">
                <p>Hi {user_name},</p>

                <p>Welcome aboard! We're thrilled to have you join our community of singles looking for meaningful connections.</p>

                <div class="features">
                    <div class="feature">
                        <strong>👥 Meet New People</strong><br>
                        Connect with singles nearby who share your interests
                    </div>
                    <div class="feature">
                        <strong>Heart Swipe to Match</strong><br>
                        Like profiles you love, pass on the ones you don't
                    </div>
                    <div class="feature">
                        <strong>💬 Chat Instantly</strong><br>
                        Start meaningful conversations with your matches
                    </div>
                </div>

                <p>Ready to find your perfect match? Start swiping now!</p>

                <div style="text-align: center;">
                    <a href="#" class="cta-button">Start Swiping</a>
                </div>
            </div>

            <div class="footer">
                <p>Happy matching! Star<br>The Dating App Team</p>
            </div>
        </div>
    </body>
    </html>
    """

    text_content = f"""
    Welcome to Dating App!

    Hi {user_name},

    Welcome aboard! We're thrilled to have you join our community.

    Here's what you can do:
    - Meet new people nearby
    - Swipe to match
    - Chat instantly with your matches

    Happy matching!
    The Dating App Team
    """

    return send_email(to_email, subject, html_content, text_content)
