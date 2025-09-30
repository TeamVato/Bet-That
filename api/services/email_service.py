"""
Email notification service for bet resolution updates
"""

import logging
from typing import Optional, List
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import os

from ..models import Bet, User

logger = logging.getLogger(__name__)

class EmailService:
    """Service for sending email notifications"""
    
    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_username = os.getenv("SMTP_USERNAME")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        self.from_email = os.getenv("FROM_EMAIL", "noreply@betthat.com")
        self.from_name = os.getenv("FROM_NAME", "Bet That")
        
        # Check if email is configured
        self.is_configured = bool(self.smtp_username and self.smtp_password)
        
        if not self.is_configured:
            logger.warning("Email service not configured. Set SMTP_USERNAME and SMTP_PASSWORD environment variables.")
    
    def send_bet_resolution_email(
        self,
        bet: Bet,
        user: User,
        result: str,
        resolution_notes: Optional[str] = None
    ) -> bool:
        """Send email notification for bet resolution"""
        if not self.is_configured:
            logger.info("Email service not configured, skipping email notification")
            return False
        
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = user.email
            msg['Subject'] = f"Bet Resolution Update - {result.upper()}"
            
            # Create email body
            body = self._create_resolution_email_body(bet, result, resolution_notes)
            msg.attach(MIMEText(body, 'html'))
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            
            logger.info(f"Resolution email sent to {user.email} for bet {bet.id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send resolution email to {user.email}: {e}")
            return False
    
    def send_bet_dispute_email(
        self,
        bet: Bet,
        user: User,
        dispute_reason: str
    ) -> bool:
        """Send email notification for bet dispute"""
        if not self.is_configured:
            logger.info("Email service not configured, skipping email notification")
            return False
        
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = user.email
            msg['Subject'] = "Bet Dispute Notification"
            
            # Create email body
            body = self._create_dispute_email_body(bet, dispute_reason)
            msg.attach(MIMEText(body, 'html'))
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            
            logger.info(f"Dispute email sent to {user.email} for bet {bet.id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send dispute email to {user.email}: {e}")
            return False
    
    def _create_resolution_email_body(
        self,
        bet: Bet,
        result: str,
        resolution_notes: Optional[str]
    ) -> str:
        """Create HTML email body for bet resolution"""
        result_emoji = {
            'win': '🎉',
            'loss': '😞',
            'push': '🤝',
            'void': '🔄'
        }.get(result, '📝')
        
        result_color = {
            'win': '#10B981',
            'loss': '#EF4444',
            'push': '#F59E0B',
            'void': '#6B7280'
        }.get(result, '#6B7280')
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Bet Resolution Update</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #1F2937; color: white; padding: 20px; text-align: center; }}
                .content {{ background: #F9FAFB; padding: 30px; }}
                .bet-details {{ background: white; padding: 20px; border-radius: 8px; margin: 20px 0; }}
                .result-badge {{ 
                    display: inline-block; 
                    padding: 8px 16px; 
                    border-radius: 20px; 
                    color: white; 
                    font-weight: bold;
                    background-color: {result_color};
                }}
                .footer {{ text-align: center; padding: 20px; color: #6B7280; font-size: 14px; }}
                .button {{ 
                    display: inline-block; 
                    padding: 12px 24px; 
                    background: #3B82F6; 
                    color: white; 
                    text-decoration: none; 
                    border-radius: 6px; 
                    margin: 20px 0;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Bet Resolution Update {result_emoji}</h1>
                </div>
                
                <div class="content">
                    <h2>Your bet has been resolved!</h2>
                    
                    <div class="bet-details">
                        <h3>Bet Details</h3>
                        <p><strong>Game:</strong> {bet.game_name or 'N/A'}</p>
                        <p><strong>Market:</strong> {bet.market}</p>
                        <p><strong>Selection:</strong> {bet.selection}</p>
                        <p><strong>Stake:</strong> ${bet.stake}</p>
                        <p><strong>Odds:</strong> {bet.odds}</p>
                        <p><strong>Result:</strong> <span class="result-badge">{result.upper()}</span></p>
                        
                        {f'<p><strong>Resolution Notes:</strong> {resolution_notes}</p>' if resolution_notes else ''}
                    </div>
                    
                    <p>You can view the full details of this bet and your betting history by clicking the button below.</p>
                    
                    <a href="https://betthat.com/bets/{bet.id}" class="button">View Bet Details</a>
                </div>
                
                <div class="footer">
                    <p>This is an automated message from Bet That. Please do not reply to this email.</p>
                    <p>If you have any questions, please contact our support team.</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _create_dispute_email_body(
        self,
        bet: Bet,
        dispute_reason: str
    ) -> str:
        """Create HTML email body for bet dispute"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Bet Dispute Notification</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #F59E0B; color: white; padding: 20px; text-align: center; }}
                .content {{ background: #F9FAFB; padding: 30px; }}
                .bet-details {{ background: white; padding: 20px; border-radius: 8px; margin: 20px 0; }}
                .dispute-reason {{ background: #FEF3C7; padding: 15px; border-radius: 6px; margin: 15px 0; }}
                .footer {{ text-align: center; padding: 20px; color: #6B7280; font-size: 14px; }}
                .button {{ 
                    display: inline-block; 
                    padding: 12px 24px; 
                    background: #3B82F6; 
                    color: white; 
                    text-decoration: none; 
                    border-radius: 6px; 
                    margin: 20px 0;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>⚠️ Bet Dispute Notification</h1>
                </div>
                
                <div class="content">
                    <h2>A dispute has been raised for your bet</h2>
                    
                    <div class="bet-details">
                        <h3>Bet Details</h3>
                        <p><strong>Game:</strong> {bet.game_name or 'N/A'}</p>
                        <p><strong>Market:</strong> {bet.market}</p>
                        <p><strong>Selection:</strong> {bet.selection}</p>
                        <p><strong>Stake:</strong> ${bet.stake}</p>
                        <p><strong>Odds:</strong> {bet.odds}</p>
                    </div>
                    
                    <div class="dispute-reason">
                        <h4>Dispute Reason:</h4>
                        <p>{dispute_reason}</p>
                    </div>
                    
                    <p>Our team will review this dispute and provide a resolution. You will be notified once the dispute has been resolved.</p>
                    
                    <a href="https://betthat.com/bets/{bet.id}/dispute" class="button">Review Dispute</a>
                </div>
                
                <div class="footer">
                    <p>This is an automated message from Bet That. Please do not reply to this email.</p>
                    <p>If you have any questions, please contact our support team.</p>
                </div>
            </div>
        </body>
        </html>
        """

# Global email service instance
email_service = EmailService()

# Convenience functions
def send_bet_resolution_notification(
    bet: Bet,
    user: User,
    result: str,
    resolution_notes: Optional[str] = None
) -> bool:
    """Send bet resolution email notification"""
    return email_service.send_bet_resolution_email(bet, user, result, resolution_notes)

def send_bet_dispute_notification(
    bet: Bet,
    user: User,
    dispute_reason: str
) -> bool:
    """Send bet dispute email notification"""
    return email_service.send_bet_dispute_email(bet, user, dispute_reason)

