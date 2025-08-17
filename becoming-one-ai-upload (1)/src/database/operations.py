"""
Database operations for Supabase integration
"""
import os
from typing import Optional, Dict, Any, List
from supabase import create_client, Client
from .models import IdentityRegistry, EventLog, ChannelMapping
import uuid


class SupabaseClient:
    """Wrapper for Supabase operations"""
    
    def __init__(self):
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_ANON_KEY")
        
        if not url or not key:
            raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY must be set")
        
        self.client: Client = create_client(url, key)
    
    async def get_or_create_person_id(
        self, 
        channel_type: str, 
        channel_id: str,
        name: Optional[str] = None
    ) -> uuid.UUID:
        """
        Get existing person_id or create new identity for a channel
        This is the core identity resolution function
        """
        # First, check if channel mapping exists
        mapping_result = self.client.table("channel_mapping").select("person_id").eq(
            "channel_type", channel_type
        ).eq("channel_id", channel_id).execute()
        
        if mapping_result.data:
            return uuid.UUID(mapping_result.data[0]["person_id"])
        
        # Create new identity
        identity_data = {
            "name": name,
            "channel_ids": {channel_type: channel_id},
            "consent": False  # Default to false, user must explicitly consent
        }
        
        identity_result = self.client.table("identity_registry").insert(
            identity_data
        ).execute()
        
        person_id = uuid.UUID(identity_result.data[0]["person_id"])
        
        # Create channel mapping
        mapping_data = {
            "channel_type": channel_type,
            "channel_id": channel_id,
            "person_id": str(person_id)
        }
        
        self.client.table("channel_mapping").insert(mapping_data).execute()
        
        return person_id
    
    async def log_event(
        self,
        person_id: Optional[uuid.UUID],
        event_type: str,
        content: Optional[str],
        source: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> uuid.UUID:
        """Log an event to the event_log table"""
        event_data = {
            "person_id": str(person_id) if person_id else None,
            "type": event_type,
            "content": content,
            "source": source,
            "metadata": metadata or {}
        }
        
        result = self.client.table("event_log").insert(event_data).execute()
        return uuid.UUID(result.data[0]["event_id"])
    
    async def get_user_history(
        self, 
        person_id: uuid.UUID, 
        limit: int = 50,
        event_types: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Get user's interaction history"""
        query = self.client.table("event_log").select("*").eq(
            "person_id", str(person_id)
        ).order("timestamp", desc=True).limit(limit)
        
        if event_types:
            query = query.in_("type", event_types)
        
        result = query.execute()
        return result.data
    
    async def update_user_consent(self, person_id: uuid.UUID, consent: bool) -> bool:
        """Update user's consent status"""
        result = self.client.table("identity_registry").update({
            "consent": consent
        }).eq("person_id", str(person_id)).execute()
        
        return len(result.data) > 0
    
    async def get_user_profile(self, person_id: uuid.UUID) -> Optional[Dict[str, Any]]:
        """Get user's complete profile"""
        result = self.client.table("identity_registry").select("*").eq(
            "person_id", str(person_id)
        ).execute()
        
        if result.data:
            return result.data[0]
        return None
    
    async def search_events_by_content(
        self, 
        search_term: str, 
        person_id: Optional[uuid.UUID] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Search events by content (for context retrieval)"""
        query = self.client.table("event_log").select("*").ilike(
            "content", f"%{search_term}%"
        ).limit(limit)
        
        if person_id:
            query = query.eq("person_id", str(person_id))
        
        result = query.execute()
        return result.data
    
    async def get_channel_stats(self) -> Dict[str, Any]:
        """Get statistics about channel usage"""
        # Get total users per channel
        channel_stats = self.client.table("channel_mapping").select(
            "channel_type"
        ).execute()
        
        # Count events per source
        event_stats = self.client.table("event_log").select(
            "source"
        ).execute()
        
        # Process and return stats
        channels = {}
        for row in channel_stats.data:
            channel_type = row["channel_type"]
            channels[channel_type] = channels.get(channel_type, 0) + 1
        
        sources = {}
        for row in event_stats.data:
            source = row["source"]
            sources[source] = sources.get(source, 0) + 1
        
        return {
            "total_users": len(channel_stats.data),
            "users_per_channel": channels,
            "events_per_source": sources
        }


# Global instance
db = SupabaseClient()
