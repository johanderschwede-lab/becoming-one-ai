"""
Supabase database models for Becoming One™ AI Journey System
"""
from datetime import datetime
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
import uuid


class IdentityRegistry(BaseModel):
    """User identity across all platforms"""
    person_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    channel_ids: Dict[str, str] = Field(default_factory=dict)  # {"telegram": "123456", "email": "user@example.com"}
    name: Optional[str] = None
    consent: bool = False
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            uuid.UUID: lambda v: str(v)
        }


class EventLog(BaseModel):
    """All system interactions and events"""
    event_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    person_id: Optional[uuid.UUID] = None
    type: str  # 'message', 'query', 'response', 'system'
    content: Optional[str] = None
    source: str  # 'telegram', 'email', 'youtube', etc.
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            uuid.UUID: lambda v: str(v)
        }


class ChannelMapping(BaseModel):
    """Maps platform-specific IDs to person_id"""
    mapping_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    channel_type: str  # 'telegram', 'email', 'youtube'
    channel_id: str  # platform-specific user ID
    person_id: uuid.UUID
    created_at: datetime = Field(default_factory=datetime.now)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            uuid.UUID: lambda v: str(v)
        }


class BecomingOneProfile(BaseModel):
    """User's journey profile and personalization data"""
    profile_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    person_id: uuid.UUID
    current_stage: str = "discovery"  # discovery, exploration, integration, mastery
    personality_traits: Dict[str, float] = Field(default_factory=dict)
    learning_preferences: Dict[str, Any] = Field(default_factory=dict)
    progress_markers: List[str] = Field(default_factory=list)
    last_interaction: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            uuid.UUID: lambda v: str(v)
        }


# Utility functions for common queries
def create_event_log_entry(
    person_id: Optional[uuid.UUID],
    event_type: str,
    content: Optional[str],
    source: str,
    metadata: Optional[Dict[str, Any]] = None
) -> EventLog:
    """Create a new event log entry"""
    return EventLog(
        person_id=person_id,
        type=event_type,
        content=content,
        source=source,
        metadata=metadata or {}
    )


def create_identity_registry_entry(
    name: Optional[str] = None,
    channel_ids: Optional[Dict[str, str]] = None,
    consent: bool = False
) -> IdentityRegistry:
    """Create a new identity registry entry"""
    return IdentityRegistry(
        name=name,
        channel_ids=channel_ids or {},
        consent=consent
    )
