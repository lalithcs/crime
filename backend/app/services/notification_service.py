import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List
import os

class NotificationService:
    """Send email/SMS notifications for crime alerts"""
    
    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.sender_email = os.getenv("SENDER_EMAIL", "")
        self.sender_password = os.getenv("SENDER_PASSWORD", "")
    
    def send_email_alert(self, recipient_email: str, alert_title: str, alert_message: str, location: str):
        """Send email notification for crime alert"""
        try:
            if not self.sender_email or not self.sender_password:
                print("Email credentials not configured")
                return False
                
            message = MIMEMultipart("alternative")
            message["Subject"] = f"🚨 Crime Alert: {alert_title}"
            message["From"] = self.sender_email
            message["To"] = recipient_email
            
            html = f"""
            <html>
                <body style="font-family: Arial, sans-serif; padding: 20px;">
                    <h2 style="color: #e53e3e;">🚨 Crime Safety Alert</h2>
                    <h3>{alert_title}</h3>
                    <p><strong>Location:</strong> {location}</p>
                    <p>{alert_message}</p>
                    <hr>
                    <p style="color: #666; font-size: 12px;">
                        This is an automated alert from CrimeScope.
                        Stay safe and be vigilant.
                    </p>
                </body>
            </html>
            """
            
            part = MIMEText(html, "html")
            message.attach(part)
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.sendmail(self.sender_email, recipient_email, message.as_string())
            
            print(f"Alert email sent to {recipient_email}")
            return True
            
        except Exception as e:
            print(f"Failed to send email: {e}")
            return False
    
    def send_sms_alert(self, phone_number: str, alert_message: str):
        """Send SMS alert (placeholder - integrate with Twilio/AWS SNS)"""
        # TODO: Integrate with Twilio or AWS SNS for SMS
        print(f"SMS alert to {phone_number}: {alert_message}")
        return True

notification_service = NotificationService()
