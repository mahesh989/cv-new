"""
Email service for sending verification and notification emails
"""
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
import logging
from app.config import settings

logger = logging.getLogger(__name__)

class EmailService:
    """Service for sending emails"""
    
    def __init__(self):
        self.smtp_server = getattr(settings, 'SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = getattr(settings, 'SMTP_PORT', 587)
        self.smtp_username = getattr(settings, 'SMTP_USERNAME', '')
        self.smtp_password = getattr(settings, 'SMTP_PASSWORD', '').replace(' ', '')  # Remove spaces
        self.from_email = getattr(settings, 'FROM_EMAIL', 'noreply@cvagent.com')
        self.from_name = getattr(settings, 'FROM_NAME', 'CV Agent')
        self.email_enabled = getattr(settings, 'EMAIL_ENABLED', True)
        self.console_output = getattr(settings, 'EMAIL_CONSOLE_OUTPUT', True)
        self.mock_success = getattr(settings, 'EMAIL_MOCK_SUCCESS', True)
    
    def send_verification_email(self, user_email: str, user_name: str, verification_token: str) -> bool:
        """Send email verification link to user"""
        try:
            # Create verification link
            verification_url = f"{settings.FRONTEND_URL}/verify-email?token={verification_token}"
            
            # Create email content
            subject = "Verify Your Email - CV Agent"
            
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Email Verification</title>
                <style>
                    body {{
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                        line-height: 1.6;
                        color: #333;
                        max-width: 600px;
                        margin: 0 auto;
                        padding: 20px;
                        background-color: #f4f4f4;
                    }}
                    .container {{
                        background-color: white;
                        padding: 30px;
                        border-radius: 10px;
                        box-shadow: 0 0 20px rgba(0,0,0,0.1);
                    }}
                    .header {{
                        text-align: center;
                        margin-bottom: 30px;
                    }}
                    .logo {{
                        font-size: 28px;
                        font-weight: bold;
                        color: #20B2AA;
                        margin-bottom: 10px;
                    }}
                    .title {{
                        font-size: 24px;
                        color: #333;
                        margin-bottom: 20px;
                    }}
                    .content {{
                        margin-bottom: 30px;
                    }}
                    .button {{
                        display: inline-block;
                        background: linear-gradient(135deg, #20B2AA, #17a2b8);
                        color: white;
                        padding: 15px 30px;
                        text-decoration: none;
                        border-radius: 5px;
                        font-weight: bold;
                        text-align: center;
                        margin: 20px 0;
                    }}
                    .button:hover {{
                        background: linear-gradient(135deg, #17a2b8, #20B2AA);
                    }}
                    .footer {{
                        margin-top: 30px;
                        padding-top: 20px;
                        border-top: 1px solid #eee;
                        font-size: 14px;
                        color: #666;
                        text-align: center;
                    }}
                    .warning {{
                        background-color: #fff3cd;
                        border: 1px solid #ffeaa7;
                        color: #856404;
                        padding: 15px;
                        border-radius: 5px;
                        margin: 20px 0;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <div class="logo">📄 CV Agent</div>
                        <h1 class="title">Verify Your Email Address</h1>
                    </div>
                    
                    <div class="content">
                        <p>Hello <strong>{user_name}</strong>,</p>
                        
                        <p>Welcome to CV Agent! We're excited to have you on board. To complete your registration and start optimizing your resume with AI, please verify your email address.</p>
                        
                        <p>Click the button below to verify your email:</p>
                        
                        <div style="text-align: center;">
                            <a href="{verification_url}" class="button">Verify Email Address</a>
                        </div>
                        
                        <div class="warning">
                            <strong>⚠️ Important:</strong> This verification link will expire in 24 hours. If you don't verify your email within this time, you'll need to register again.
                        </div>
                        
                        <p>If the button doesn't work, you can copy and paste this link into your browser:</p>
                        <p style="word-break: break-all; background-color: #f8f9fa; padding: 10px; border-radius: 5px; font-family: monospace;">
                            {verification_url}
                        </p>
                        
                        <p>Once verified, you'll be able to:</p>
                        <ul>
                            <li>✅ Upload and analyze your CV</li>
                            <li>✅ Get AI-powered recommendations</li>
                            <li>✅ Create tailored resumes for specific jobs</li>
                            <li>✅ Track your application success</li>
                        </ul>
                    </div>
                    
                    <div class="footer">
                        <p>If you didn't create an account with CV Agent, please ignore this email.</p>
                        <p>This email was sent to {user_email}</p>
                        <p>&copy; 2024 CV Agent. All rights reserved.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            text_content = f"""
            Hello {user_name},
            
            Welcome to CV Agent! Please verify your email address to complete your registration.
            
            Click this link to verify: {verification_url}
            
            This link will expire in 24 hours.
            
            If you didn't create an account with CV Agent, please ignore this email.
            
            Best regards,
            CV Agent Team
            """
            
            # Send email
            return self._send_email(user_email, subject, text_content, html_content)
            
        except Exception as e:
            logger.error(f"Failed to send verification email: {e}")
            return False
    
    def send_welcome_email(self, user_email: str, user_name: str) -> bool:
        """Send welcome email after successful verification"""
        try:
            subject = "Welcome to CV Agent - Your Account is Verified!"
            
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Welcome to CV Agent</title>
                <style>
                    body {{
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                        line-height: 1.6;
                        color: #333;
                        max-width: 600px;
                        margin: 0 auto;
                        padding: 20px;
                        background-color: #f4f4f4;
                    }}
                    .container {{
                        background-color: white;
                        padding: 30px;
                        border-radius: 10px;
                        box-shadow: 0 0 20px rgba(0,0,0,0.1);
                    }}
                    .header {{
                        text-align: center;
                        margin-bottom: 30px;
                    }}
                    .logo {{
                        font-size: 28px;
                        font-weight: bold;
                        color: #20B2AA;
                        margin-bottom: 10px;
                    }}
                    .success {{
                        background-color: #d4edda;
                        border: 1px solid #c3e6cb;
                        color: #155724;
                        padding: 15px;
                        border-radius: 5px;
                        margin: 20px 0;
                        text-align: center;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <div class="logo">📄 CV Agent</div>
                        <h1>Welcome to CV Agent!</h1>
                    </div>
                    
                    <div class="success">
                        <strong>🎉 Your email has been verified successfully!</strong>
                    </div>
                    
                    <p>Hello <strong>{user_name}</strong>,</p>
                    
                    <p>Your CV Agent account is now active and ready to use! You can now:</p>
                    
                    <ul>
                        <li>📤 Upload your CV for AI analysis</li>
                        <li>🎯 Get personalized recommendations</li>
                        <li>✏️ Create tailored resumes for specific jobs</li>
                        <li>📊 Track your application success</li>
                    </ul>
                    
                    <p>Ready to get started? Log in to your account and upload your first CV!</p>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{settings.FRONTEND_URL}/login" style="display: inline-block; background: linear-gradient(135deg, #20B2AA, #17a2b8); color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-weight: bold;">Get Started</a>
                    </div>
                    
                    <p>If you have any questions, feel free to reach out to our support team.</p>
                    
                    <p>Best regards,<br>CV Agent Team</p>
                </div>
            </body>
            </html>
            """
            
            text_content = f"""
            Hello {user_name},
            
            🎉 Your email has been verified successfully!
            
            Your CV Agent account is now active and ready to use!
            
            You can now:
            - Upload your CV for AI analysis
            - Get personalized recommendations  
            - Create tailored resumes for specific jobs
            - Track your application success
            
            Ready to get started? Log in to your account and upload your first CV!
            
            Best regards,
            CV Agent Team
            """
            
            return self._send_email(user_email, subject, text_content, html_content)
            
        except Exception as e:
            logger.error(f"Failed to send welcome email: {e}")
            return False
    
    def _send_email(self, to_email: str, subject: str, text_content: str, html_content: str) -> bool:
        """Send email using SMTP with console output for debugging"""
        try:
            # Console output for debugging
            if self.console_output:
                print(f"\n📧 EMAIL DEBUG OUTPUT:")
                print(f"   To: {to_email}")
                print(f"   From: {self.from_name} <{self.from_email}>")
                print(f"   Subject: {subject}")
                print(f"   SMTP Server: {self.smtp_server}:{self.smtp_port}")
                print(f"   Username: {self.smtp_username}")
                print(f"   Password: {'*' * len(self.smtp_password) if self.smtp_password else 'NOT SET'}")
                print(f"   Email Enabled: {self.email_enabled}")
                print(f"   Text Content: {text_content[:200]}...")
            
            # If email is disabled, just log and return success
            if not self.email_enabled:
                logger.info(f"Email sending disabled - would send to {to_email}")
                print(f"   ✅ Email sending disabled - simulated success")
                print(f"   📧 DEVELOPMENT MODE: Email content logged above")
                return self.mock_success
            
            # Check if credentials are configured
            if not self.smtp_username or not self.smtp_password:
                logger.error("SMTP credentials not configured")
                print(f"   ❌ SMTP credentials not configured!")
                return False
            
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = f"{self.from_name} <{self.from_email}>"
            message["To"] = to_email
            
            # Create text and HTML parts
            text_part = MIMEText(text_content, "plain")
            html_part = MIMEText(html_content, "html")
            
            # Attach parts
            message.attach(text_part)
            message.attach(html_part)
            
            # Create secure connection and send email
            context = ssl.create_default_context()
            
            print(f"   🔄 Connecting to SMTP server...")
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)
                print(f"   🔐 Authenticating with credentials...")
                server.login(self.smtp_username, self.smtp_password)
                print(f"   📤 Sending email...")
                server.sendmail(self.from_email, to_email, message.as_string())
            
            logger.info(f"Email sent successfully to {to_email}")
            print(f"   ✅ Email sent successfully!")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            print(f"   ❌ Email failed: {e}")
            return False

# Create global instance
email_service = EmailService()