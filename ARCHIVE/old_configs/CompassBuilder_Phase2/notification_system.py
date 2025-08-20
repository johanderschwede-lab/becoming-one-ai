import os
import json
import logging
import requests
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

@dataclass
class NotificationContent:
    title: str
    content: str
    category: str
    score: float
    decision: str
    file_path: str
    export_path: str
    keywords: List[str]
    timestamp: str

class NotificationSystem:
    def __init__(self):
        # Telegram Bot Configuration
        self.telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")  # Your personal chat ID
        
        # Email Configuration
        self.email_enabled = os.getenv("EMAIL_NOTIFICATIONS", "false").lower() == "true"
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.email_user = os.getenv("EMAIL_USER")
        self.email_password = os.getenv("EMAIL_PASSWORD")
        self.email_recipient = os.getenv("EMAIL_RECIPIENT")
        
        # Notification preferences
        self.notify_on_compass_core = True
        self.notify_on_high_score = True
        self.notify_on_master_prompt = True
        self.min_score_threshold = 7.0  # Only notify for high-quality content
        
        logging.info("Notification system initialized")

    def send_telegram_notification(self, notification: NotificationContent) -> bool:
        """Send notification via Telegram"""
        if not self.telegram_bot_token or not self.telegram_chat_id:
            logging.warning("Telegram credentials not configured")
            return False
        
        try:
            # Create message
            message = self._format_telegram_message(notification)
            
            # Send via Telegram Bot API
            url = f"https://api.telegram.org/bot{self.telegram_bot_token}/sendMessage"
            data = {
                "chat_id": self.telegram_chat_id,
                "text": message,
                "parse_mode": "Markdown"
            }
            
            response = requests.post(url, json=data, timeout=10)
            
            if response.status_code == 200:
                logging.info(f"Telegram notification sent successfully")
                return True
            else:
                logging.error(f"Telegram notification failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logging.error(f"Error sending Telegram notification: {str(e)}")
            return False

    def send_email_notification(self, notification: NotificationContent) -> bool:
        """Send notification via email"""
        if not self.email_enabled or not all([self.email_user, self.email_password, self.email_recipient]):
            logging.warning("Email notifications not configured")
            return False
        
        try:
            # Create email
            msg = MIMEMultipart()
            msg['From'] = self.email_user
            msg['To'] = self.email_recipient
            msg['Subject'] = f"🎯 Compass Core Update: {notification.title}"
            
            # Create email body
            body = self._format_email_message(notification)
            msg.attach(MIMEText(body, 'html'))
            
            # Send email
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email_user, self.email_password)
            server.send_message(msg)
            server.quit()
            
            logging.info(f"Email notification sent successfully to {self.email_recipient}")
            return True
            
        except Exception as e:
            logging.error(f"Error sending email notification: {str(e)}")
            return False

    def _format_telegram_message(self, notification: NotificationContent) -> str:
        """Format message for Telegram"""
        emoji_map = {
            "method_model": "🧠",
            "prompt_module": "🎯",
            "platform": "⚙️",
            "offer": "💎",
            "tone": "🎨",
            "community": "👥",
            "content": "📄",
            "research": "🔬",
            "strategy": "📊"
        }
        
        emoji = emoji_map.get(notification.category, "📝")
        
        message = f"""
🎯 *COMPASS CORE UPDATE*

{emoji} *{notification.title}*

📊 *Score:* {notification.score}/10
🏷️ *Category:* {notification.category}
✅ *Decision:* {notification.decision}
📁 *Location:* {notification.export_path}

🔑 *Key Terms:* {', '.join(notification.keywords[:5])}

⏰ *Processed:* {notification.timestamp}

Your content has been added to the Compass Core! 🎉
        """
        
        return message.strip()

    def _format_email_message(self, notification: NotificationContent) -> str:
        """Format message for email"""
        emoji_map = {
            "method_model": "🧠",
            "prompt_module": "🎯",
            "platform": "⚙️",
            "offer": "💎",
            "tone": "🎨",
            "community": "👥",
            "content": "📄",
            "research": "🔬",
            "strategy": "📊"
        }
        
        emoji = emoji_map.get(notification.category, "📝")
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background-color: #f0f8ff; padding: 20px; border-radius: 10px; }}
        .content {{ margin: 20px 0; }}
        .score {{ font-size: 24px; color: #2e8b57; font-weight: bold; }}
        .category {{ background-color: #e6f3ff; padding: 10px; border-radius: 5px; }}
        .keywords {{ background-color: #f9f9f9; padding: 10px; border-radius: 5px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🎯 Compass Core Update</h1>
        <p>New content has been added to your master prompt system!</p>
    </div>
    
    <div class="content">
        <h2>{emoji} {notification.title}</h2>
        
        <div class="score">
            Quality Score: {notification.score}/10
        </div>
        
        <div class="category">
            <strong>Category:</strong> {notification.category}<br>
            <strong>Decision:</strong> {notification.decision}<br>
            <strong>Location:</strong> {notification.export_path}
        </div>
        
        <div class="keywords">
            <strong>Key Terms:</strong> {', '.join(notification.keywords[:8])}
        </div>
        
        <p><strong>Processed:</strong> {notification.timestamp}</p>
        
        <p>This content is now part of your master prompt and will be used by your AI systems.</p>
    </div>
</body>
</html>
        """
        
        return html

    def should_notify(self, notification: NotificationContent) -> bool:
        """Determine if notification should be sent"""
        # Always notify for Compass Core additions
        if "COMPASS_CORE" in notification.export_path:
            return True
        
        # Notify for high-quality content
        if notification.score >= self.min_score_threshold:
            return True
        
        # Notify for master prompt related content
        if "master_prompt" in notification.category.lower():
            return True
        
        return False

    def notify_compass_core_update(self, classification: Dict, strategic_score: Dict, 
                                 file_path: str, export_path: str) -> bool:
        """Send notification for Compass Core updates"""
        
        # Create notification content
        notification = NotificationContent(
            title=os.path.basename(file_path),
            content="Content added to Compass Core",
            category=classification.get("primary_category", "unknown"),
            score=strategic_score.get("total_score", 0),
            decision=strategic_score.get("processing_decision", "unknown"),
            file_path=file_path,
            export_path=export_path,
            keywords=classification.get("keywords_found", [])[:8],
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        
        # Check if we should notify
        if not self.should_notify(notification):
            logging.info(f"No notification sent for {file_path} (score: {notification.score})")
            return False
        
        # Send notifications
        telegram_sent = self.send_telegram_notification(notification)
        email_sent = self.send_email_notification(notification)
        
        logging.info(f"Notifications sent - Telegram: {telegram_sent}, Email: {email_sent}")
        return telegram_sent or email_sent

    def send_daily_summary(self, processed_files: List[Dict]) -> bool:
        """Send daily summary of processed content"""
        if not processed_files:
            return False
        
        # Group by category
        by_category = {}
        for file_info in processed_files:
            category = file_info.get("category", "unknown")
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(file_info)
        
        # Create summary
        summary = f"""
📊 *DAILY COMPASS PROCESSING SUMMARY*

📅 Date: {datetime.now().strftime("%Y-%m-%d")}
📁 Total Files Processed: {len(processed_files)}

📂 *By Category:*
"""
        
        for category, files in by_category.items():
            summary += f"• {category}: {len(files)} files\n"
        
        summary += f"\n🎯 *High-Quality Content:* {len([f for f in processed_files if f.get('score', 0) >= 7.0])} files"
        summary += f"\n📚 *Added to Compass Core:* {len([f for f in processed_files if 'COMPASS_CORE' in f.get('export_path', '')])} files"
        
        # Send summary
        if self.telegram_bot_token and self.telegram_chat_id:
            url = f"https://api.telegram.org/bot{self.telegram_bot_token}/sendMessage"
            data = {
                "chat_id": self.telegram_chat_id,
                "text": summary,
                "parse_mode": "Markdown"
            }
            
            try:
                response = requests.post(url, json=data, timeout=10)
                return response.status_code == 200
            except Exception as e:
                logging.error(f"Error sending daily summary: {str(e)}")
                return False
        
        return False

    def test_notifications(self) -> Dict[str, bool]:
        """Test notification system"""
        test_notification = NotificationContent(
            title="Test Document",
            content="This is a test notification",
            category="method_model",
            score=8.5,
            decision="SAFE_CORE - Add directly to Compass core",
            file_path="test_file.md",
            export_path="COMPASS_CORE/method_model",
            keywords=["emotional anchor", "stance", "nervous system"],
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        
        results = {
            "telegram": self.send_telegram_notification(test_notification),
            "email": self.send_email_notification(test_notification)
        }
        
        return results

# Example usage
if __name__ == "__main__":
    # Test the notification system
    notifier = NotificationSystem()
    
    # Test notifications
    results = notifier.test_notifications()
    print(f"Notification test results: {results}")
    
    # Example of processing a file
    classification = {
        "primary_category": "method_model",
        "keywords_found": ["emotional anchor", "stance", "nervous system", "digest"]
    }
    
    strategic_score = {
        "total_score": 8.5,
        "processing_decision": "SAFE_CORE - Add directly to Compass core"
    }
    
    success = notifier.notify_compass_core_update(
        classification, strategic_score, 
        "test_method.md", "COMPASS_CORE/method_model"
    )
    
    print(f"Notification sent: {success}")
