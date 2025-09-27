"""
Email service for sending verification and reset emails
"""
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, Dict, Any
from fastapi import HTTPException, status
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class EmailService:
    """Email service for sending verification and reset emails"""
    
    def __init__(self):
        self.smtp_server = getattr(settings, 'SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = getattr(settings, 'SMTP_PORT', 587)
        self.smtp_username = getattr(settings, 'SMTP_USERNAME', '')
        self.smtp_password = getattr(settings, 'SMTP_PASSWORD', '')
        self.from_email = getattr(settings, 'FROM_EMAIL', 'noreply@cvapp.com')
        self.from_name = getattr(settings, 'FROM_NAME', 'CV App')
    
    def send_email(self, to_email: str, subject: str, html_content: str, 
                   text_content: Optional[str] = None) -> bool:
        """Send email to recipient"""
        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = f"{self.from_name} <{self.from_email}>"
            message["To"] = to_email
            
            # Add text content if provided
            if text_content:
                text_part = MIMEText(text_content, "plain")
                message.attach(text_part)
            
            # Add HTML content
            html_part = MIMEText(html_content, "html")
            message.attach(html_part)
            
            # Send email
            context = ssl.create_default_context()
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.smtp_username, self.smtp_password)
                server.sendmail(self.from_email, to_email, message.as_string())
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False
    
    def send_verification_email(self, to_email: str, username: str, 
                              verification_token: str) -> bool:
        """Send email verification email"""
        try:
            verification_url = f"{settings.FRONTEND_URL}/verify-email?token={verification_token}"
            
            subject = "Verify Your Email Address - CV App"
            
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>Email Verification</title>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background-color: #4CAF50; color: white; padding: 20px; text-align: center; }}
                    .content {{ padding: 20px; background-color: #f9f9f9; }}
                    .button {{ display: inline-block; padding: 12px 24px; background-color: #4CAF50; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                    .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Welcome to CV App!</h1>
                    </div>
                    <div class="content">
                        <h2>Hi {username},</h2>
                        <p>Thank you for registering with CV App. To complete your registration, please verify your email address by clicking the button below:</p>
                        <a href="{verification_url}" class="button">Verify Email Address</a>
                        <p>If the button doesn't work, you can copy and paste this link into your browser:</p>
                        <p><a href="{verification_url}">{verification_url}</a></p>
                        <p>This link will expire in 24 hours for security reasons.</p>
                        <p>If you didn't create an account with CV App, please ignore this email.</p>
                    </div>
                    <div class="footer">
                        <p>© 2024 CV App. All rights reserved.</p>
                        <p>This is an automated message, please do not reply.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            text_content = f"""
            Hi {username},
            
            Thank you for registering with CV App. To complete your registration, please verify your email address by visiting this link:
            
            {verification_url}
            
            This link will expire in 24 hours for security reasons.
            
            If you didn't create an account with CV App, please ignore this email.
            
            Best regards,
            CV App Team
            """
            
            return self.send_email(to_email, subject, html_content, text_content)
            
        except Exception as e:
            logger.error(f"Failed to send verification email: {str(e)}")
            return False
    
    def send_password_reset_email(self, to_email: str, username: str, 
                                 reset_token: str) -> bool:
        """Send password reset email"""
        try:
            reset_url = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"
            
            subject = "Reset Your Password - CV App"
            
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>Password Reset</title>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background-color: #f44336; color: white; padding: 20px; text-align: center; }}
                    .content {{ padding: 20px; background-color: #f9f9f9; }}
                    .button {{ display: inline-block; padding: 12px 24px; background-color: #f44336; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                    .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
                    .warning {{ background-color: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Password Reset Request</h1>
                    </div>
                    <div class="content">
                        <h2>Hi {username},</h2>
                        <p>We received a request to reset your password for your CV App account.</p>
                        <p>To reset your password, please click the button below:</p>
                        <a href="{reset_url}" class="button">Reset Password</a>
                        <p>If the button doesn't work, you can copy and paste this link into your browser:</p>
                        <p><a href="{reset_url}">{reset_url}</a></p>
                        <div class="warning">
                            <strong>Security Notice:</strong> This link will expire in 1 hour for security reasons. If you didn't request a password reset, please ignore this email and your password will remain unchanged.
                        </div>
                    </div>
                    <div class="footer">
                        <p>© 2024 CV App. All rights reserved.</p>
                        <p>This is an automated message, please do not reply.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            text_content = f"""
            Hi {username},
            
            We received a request to reset your password for your CV App account.
            
            To reset your password, please visit this link:
            
            {reset_url}
            
            This link will expire in 1 hour for security reasons.
            
            If you didn't request a password reset, please ignore this email and your password will remain unchanged.
            
            Best regards,
            CV App Team
            """
            
            return self.send_email(to_email, subject, html_content, text_content)
            
        except Exception as e:
            logger.error(f"Failed to send password reset email: {str(e)}")
            return False
    
    def send_welcome_email(self, to_email: str, username: str) -> bool:
        """Send welcome email after successful verification"""
        try:
            subject = "Welcome to CV App!"
            
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>Welcome to CV App</title>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background-color: #4CAF50; color: white; padding: 20px; text-align: center; }}
                    .content {{ padding: 20px; background-color: #f9f9f9; }}
                    .button {{ display: inline-block; padding: 12px 24px; background-color: #4CAF50; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                    .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Welcome to CV App!</h1>
                    </div>
                    <div class="content">
                        <h2>Hi {username},</h2>
                        <p>Your email has been successfully verified! Welcome to CV App.</p>
                        <p>You can now:</p>
                        <ul>
                            <li>Upload and analyze your CVs</li>
                            <li>Get AI-powered recommendations</li>
                            <li>Match your skills with job requirements</li>
                            <li>Track your job applications</li>
                        </ul>
                        <a href="{settings.FRONTEND_URL}/dashboard" class="button">Go to Dashboard</a>
                        <p>If you have any questions, feel free to contact our support team.</p>
                    </div>
                    <div class="footer">
                        <p>© 2024 CV App. All rights reserved.</p>
                        <p>This is an automated message, please do not reply.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            text_content = f"""
            Hi {username},
            
            Your email has been successfully verified! Welcome to CV App.
            
            You can now:
            - Upload and analyze your CVs
            - Get AI-powered recommendations
            - Match your skills with job requirements
            - Track your job applications
            
            Visit your dashboard: {settings.FRONTEND_URL}/dashboard
            
            If you have any questions, feel free to contact our support team.
            
            Best regards,
            CV App Team
            """
            
            return self.send_email(to_email, subject, html_content, text_content)
            
        except Exception as e:
            logger.error(f"Failed to send welcome email: {str(e)}")
            return False
