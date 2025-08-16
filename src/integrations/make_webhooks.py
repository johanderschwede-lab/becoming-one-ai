"""
Make.com webhook integration for workflow automation
"""
import os
import aiohttp
from typing import Dict, Any, Optional
from loguru import logger


class MakeWebhookClient:
    """Client for triggering Make.com webhooks"""
    
    def __init__(self):
        self.webhook_url = os.getenv("MAKE_WEBHOOK_URL")
        self.api_token = os.getenv("MAKE_API_TOKEN")
        
        if not self.webhook_url:
            logger.warning("MAKE_WEBHOOK_URL not set - webhook triggers will be skipped")
    
    async def trigger_message_webhook(self, data: Dict[str, Any]) -> bool:
        """Trigger Make.com webhook for new messages"""
        if not self.webhook_url:
            logger.debug("Webhook URL not configured, skipping trigger")
            return False
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {}
                if self.api_token:
                    headers["Authorization"] = f"Bearer {self.api_token}"
                
                payload = {
                    "event_type": "new_message",
                    "timestamp": data.get("timestamp"),
                    **data
                }
                
                async with session.post(
                    self.webhook_url,
                    json=payload,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        logger.info("Successfully triggered Make.com webhook")
                        return True
                    else:
                        logger.error(f"Webhook failed with status {response.status}")
                        return False
                        
        except Exception as e:
            logger.error(f"Error triggering webhook: {e}")
            return False
    
    async def trigger_user_event_webhook(
        self, 
        event_type: str, 
        person_id: str, 
        data: Dict[str, Any]
    ) -> bool:
        """Trigger webhook for user events (consent, profile updates, etc.)"""
        if not self.webhook_url:
            return False
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {}
                if self.api_token:
                    headers["Authorization"] = f"Bearer {self.api_token}"
                
                payload = {
                    "event_type": event_type,
                    "person_id": person_id,
                    "data": data
                }
                
                async with session.post(
                    self.webhook_url,
                    json=payload,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    success = response.status == 200
                    if success:
                        logger.info(f"Triggered user event webhook: {event_type}")
                    else:
                        logger.error(f"User event webhook failed: {response.status}")
                    return success
                    
        except Exception as e:
            logger.error(f"Error triggering user event webhook: {e}")
            return False
    
    async def send_analytics_data(self, analytics: Dict[str, Any]) -> bool:
        """Send analytics data to Make.com for processing"""
        if not self.webhook_url:
            return False
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {}
                if self.api_token:
                    headers["Authorization"] = f"Bearer {self.api_token}"
                
                payload = {
                    "event_type": "analytics_update",
                    "analytics": analytics
                }
                
                async with session.post(
                    self.webhook_url,
                    json=payload,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    success = response.status == 200
                    if success:
                        logger.info("Sent analytics data to Make.com")
                    return success
                    
        except Exception as e:
            logger.error(f"Error sending analytics: {e}")
            return False


class MakeScenarioTrigger:
    """Trigger specific Make.com scenarios"""
    
    def __init__(self, scenario_webhook_url: str, api_token: Optional[str] = None):
        self.webhook_url = scenario_webhook_url
        self.api_token = api_token
    
    async def trigger(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Trigger a specific Make.com scenario"""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {"Content-Type": "application/json"}
                if self.api_token:
                    headers["Authorization"] = f"Bearer {self.api_token}"
                
                async with session.post(
                    self.webhook_url,
                    json=data,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    result = await response.json() if response.content_type == "application/json" else {}
                    
                    return {
                        "success": response.status == 200,
                        "status_code": response.status,
                        "data": result
                    }
                    
        except Exception as e:
            logger.error(f"Error triggering Make scenario: {e}")
            return {
                "success": False,
                "error": str(e)
            }


# Pre-configured scenario triggers for common workflows
class BecomingOneMakeScenarios:
    """Pre-configured Make.com scenarios for Becoming One™ system"""
    
    def __init__(self):
        self.base_url = os.getenv("MAKE_WEBHOOK_URL", "").rstrip("/")
        self.api_token = os.getenv("MAKE_API_TOKEN")
    
    def get_telegram_message_processor(self) -> MakeScenarioTrigger:
        """Get trigger for Telegram message processing scenario"""
        webhook_url = f"{self.base_url}/telegram-message"
        return MakeScenarioTrigger(webhook_url, self.api_token)
    
    def get_user_onboarding_trigger(self) -> MakeScenarioTrigger:
        """Get trigger for user onboarding workflow"""
        webhook_url = f"{self.base_url}/user-onboarding"
        return MakeScenarioTrigger(webhook_url, self.api_token)
    
    def get_analytics_processor(self) -> MakeScenarioTrigger:
        """Get trigger for analytics processing"""
        webhook_url = f"{self.base_url}/analytics"
        return MakeScenarioTrigger(webhook_url, self.api_token)
    
    async def process_telegram_message(
        self, 
        person_id: str, 
        message: str, 
        telegram_user_id: int,
        username: Optional[str] = None
    ) -> Dict[str, Any]:
        """Process Telegram message through Make.com scenario"""
        trigger = self.get_telegram_message_processor()
        
        data = {
            "person_id": person_id,
            "message": message,
            "telegram_user_id": telegram_user_id,
            "username": username,
            "timestamp": "{{now}}"  # Make.com will replace with current timestamp
        }
        
        return await trigger.trigger(data)
    
    async def trigger_user_onboarding(
        self, 
        person_id: str, 
        channel_type: str,
        user_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Trigger user onboarding workflow"""
        trigger = self.get_user_onboarding_trigger()
        
        data = {
            "person_id": person_id,
            "channel_type": channel_type,
            "user_info": user_info,
            "onboarding_stage": "welcome"
        }
        
        return await trigger.trigger(data)
