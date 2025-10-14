import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config import get_settings
from datetime import datetime

settings = get_settings()


class EmailService:
    
    def __init__(self):
        self.smtp_server = settings.smtp_server
        self.smtp_port = settings.smtp_port
        self.smtp_username = settings.smtp_username
        self.smtp_password = settings.smtp_password
        self.admin_email = settings.admin_email
    
    async def send_lead_notification(self, lead_data: dict, session_id: str):
        """Send email notification when a new lead is captured"""
        
        if not self._is_configured():
            print("⚠️ Email not configured - skipping notification")
            return False
        
        try:
            subject = f"🏡 New Real Estate Lead: {lead_data.get('name', 'Unknown')}"
            
            body = self._create_lead_email_body(lead_data, session_id)
            
            success = self._send_email(
                to_email=self.admin_email,
                subject=subject,
                body=body
            )
            
            if success:
                print(f"✅ Lead notification sent for session: {session_id}")
            else:
                print(f"❌ Failed to send lead notification for session: {session_id}")
            
            return success
            
        except Exception as e:
            print(f"Error sending lead notification: {e}")
            return False
    
    def _create_lead_email_body(self, lead_data: dict, session_id: str) -> str:
        """Create HTML email body for lead notification"""
        
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                           color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                .lead-info {{ background: white; padding: 20px; border-radius: 8px; margin: 20px 0; }}
                .info-row {{ padding: 10px 0; border-bottom: 1px solid #eee; }}
                .label {{ font-weight: bold; color: #667eea; display: inline-block; width: 150px; }}
                .value {{ color: #333; }}
                .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 12px; }}
                .badge {{ display: inline-block; padding: 5px 15px; background: #4CAF50; 
                         color: white; border-radius: 20px; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎯 New Lead Alert!</h1>
                    <p>A new potential customer has shown interest</p>
                </div>
                
                <div class="content">
                    <div class="lead-info">
                        <h2>Lead Information</h2>
                        
                        <div class="info-row">
                            <span class="label">Name:</span>
                            <span class="value">{lead_data.get('name', 'Not provided')}</span>
                        </div>
                        
                        <div class="info-row">
                            <span class="label">Email:</span>
                            <span class="value">{lead_data.get('email', 'Not provided')}</span>
                        </div>
                        
                        <div class="info-row">
                            <span class="label">Phone:</span>
                            <span class="value">{lead_data.get('phone', 'Not provided')}</span>
                        </div>
                        
                        <div class="info-row">
                            <span class="label">Purpose:</span>
                            <span class="value">{lead_data.get('purpose', 'Not specified')}</span>
                        </div>
                        
                        <div class="info-row">
                            <span class="label">Location:</span>
                            <span class="value">{lead_data.get('location', 'Not specified')}</span>
                        </div>
                        
                        <div class="info-row">
                            <span class="label">Budget:</span>
                            <span class="value">{lead_data.get('budget', 'Not specified')}</span>
                        </div>
                        
                        <div class="info-row">
                            <span class="label">Timeline:</span>
                            <span class="value">{lead_data.get('timeline', 'Not specified')}</span>
                        </div>
                        
                        <div class="info-row">
                            <span class="label">Property Type:</span>
                            <span class="value">{lead_data.get('property_type', 'Not specified')}</span>
                        </div>
                        
                        <div class="info-row">
                            <span class="label">Session ID:</span>
                            <span class="value" style="font-size: 11px;">{session_id}</span>
                        </div>
                        
                        <div class="info-row">
                            <span class="label">Captured At:</span>
                            <span class="value">{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</span>
                        </div>
                    </div>
                    
                    <p style="margin-top: 20px;">
                        <strong>Next Steps:</strong><br>
                        • Review the lead details<br>
                        • Contact within 24 hours for best conversion<br>
                        • Check conversation history for context
                    </p>
                </div>
                
                <div class="footer">
                    <p>This is an automated notification from DreamHome Realty Lead Chatbot</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def _send_email(self, to_email: str, subject: str, body: str) -> bool:
        """Send an email"""
        
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = self.smtp_username
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Attach HTML body
            html_part = MIMEText(body, 'html')
            msg.attach(html_part)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            
            return True
            
        except Exception as e:
            print(f"Error sending email: {e}")
            return False
    
    def _is_configured(self) -> bool:
        """Check if email is properly configured"""
        return bool(
            self.smtp_server and 
            self.smtp_username and 
            self.smtp_password and 
            self.admin_email
        )


# Singleton instance
email_service = EmailService()