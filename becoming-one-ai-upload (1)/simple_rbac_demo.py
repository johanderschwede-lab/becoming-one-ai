#!/usr/bin/env python3
"""
Simple RBAC Demo - Test the core concepts without full Supabase setup
"""

import asyncio
import os
import sys
from pathlib import Path
from enum import Enum
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from dotenv import load_dotenv
from loguru import logger


class UserTier(Enum):
    """User access tiers with increasing privileges"""
    FREE = "free"
    PREMIUM = "premium" 
    PRO = "pro"
    MASTER = "master"
    ADMIN = "admin"


class Permission(Enum):
    """Granular permissions for different system features"""
    # Basic permissions
    BASIC_CHAT = "basic_chat"
    PERSONALITY_ANALYSIS = "personality_analysis"
    EVENT_LOGGING = "event_logging"
    
    # Content access permissions
    ACCESS_SCHAUBILDER_BASIC = "access_schaubilder_basic"
    ACCESS_SCHAUBILDER_ADVANCED = "access_schaubilder_advanced"
    ACCESS_TEACHING_MATERIALS = "access_teaching_materials"
    ACCESS_MASTER_PROMPTS = "access_master_prompts"
    
    # Specialized AI agents
    ACCESS_FOURTH_WAY_AGENT = "access_fourth_way_agent"
    ACCESS_HYLOZOICS_AGENT = "access_hylozoics_agent"
    ACCESS_NEVILLE_AGENT = "access_neville_agent"
    ACCESS_AMANITA_RESEARCH_AGENT = "access_amanita_research_agent"
    
    # Advanced features
    VOICE_ANALYSIS = "voice_analysis"
    VIDEO_ANALYSIS = "video_analysis"
    CUSTOM_PERSONALITY_REPORTS = "custom_personality_reports"
    PRACTITIONER_TOOLS = "practitioner_tools"
    
    # Community features
    PREMIUM_GROUPS = "premium_groups"
    MASTER_GROUPS = "master_groups"
    MENTORSHIP_ACCESS = "mentorship_access"


@dataclass
class UserProfile:
    """User profile with tier and permissions"""
    person_id: str
    email: str
    name: str
    tier: UserTier
    permissions: List[Permission]
    subscription_status: str
    subscription_expires: Optional[datetime]
    is_active: bool = True


class SimpleRBAC:
    """Simple RBAC system for demonstration"""
    
    # Tier-based permission mapping
    TIER_PERMISSIONS = {
        UserTier.FREE: [
            Permission.BASIC_CHAT,
            Permission.PERSONALITY_ANALYSIS,
            Permission.EVENT_LOGGING,
        ],
        UserTier.PREMIUM: [
            Permission.BASIC_CHAT,
            Permission.PERSONALITY_ANALYSIS,
            Permission.EVENT_LOGGING,
            Permission.ACCESS_SCHAUBILDER_BASIC,
            Permission.VOICE_ANALYSIS,
            Permission.PREMIUM_GROUPS,
            Permission.ACCESS_FOURTH_WAY_AGENT,
        ],
        UserTier.PRO: [
            Permission.BASIC_CHAT,
            Permission.PERSONALITY_ANALYSIS,
            Permission.EVENT_LOGGING,
            Permission.ACCESS_SCHAUBILDER_BASIC,
            Permission.ACCESS_SCHAUBILDER_ADVANCED,
            Permission.ACCESS_TEACHING_MATERIALS,
            Permission.VOICE_ANALYSIS,
            Permission.VIDEO_ANALYSIS,
            Permission.CUSTOM_PERSONALITY_REPORTS,
            Permission.PREMIUM_GROUPS,
            Permission.MASTER_GROUPS,
            Permission.ACCESS_FOURTH_WAY_AGENT,
            Permission.ACCESS_HYLOZOICS_AGENT,
            Permission.ACCESS_NEVILLE_AGENT,
        ],
        UserTier.MASTER: [
            # All PRO permissions plus:
            Permission.BASIC_CHAT,
            Permission.PERSONALITY_ANALYSIS,
            Permission.EVENT_LOGGING,
            Permission.ACCESS_SCHAUBILDER_BASIC,
            Permission.ACCESS_SCHAUBILDER_ADVANCED,
            Permission.ACCESS_TEACHING_MATERIALS,
            Permission.ACCESS_MASTER_PROMPTS,
            Permission.VOICE_ANALYSIS,
            Permission.VIDEO_ANALYSIS,
            Permission.CUSTOM_PERSONALITY_REPORTS,
            Permission.PRACTITIONER_TOOLS,
            Permission.PREMIUM_GROUPS,
            Permission.MASTER_GROUPS,
            Permission.MENTORSHIP_ACCESS,
            Permission.ACCESS_FOURTH_WAY_AGENT,
            Permission.ACCESS_HYLOZOICS_AGENT,
            Permission.ACCESS_NEVILLE_AGENT,
            Permission.ACCESS_AMANITA_RESEARCH_AGENT,
        ]
    }
    
    def __init__(self):
        self.users: Dict[str, UserProfile] = {}
        logger.info("Simple RBAC system initialized")
    
    def create_user(
        self, 
        email: str, 
        name: str, 
        tier: UserTier = UserTier.FREE
    ) -> UserProfile:
        """Create a new user profile"""
        
        person_id = f"user_{len(self.users) + 1}"
        permissions = self.TIER_PERMISSIONS.get(tier, [])
        
        # Calculate subscription expiry
        if tier == UserTier.FREE:
            subscription_status = "trial"
            subscription_expires = None
        else:
            subscription_status = "active"
            subscription_expires = datetime.now() + timedelta(days=30)
        
        user = UserProfile(
            person_id=person_id,
            email=email,
            name=name,
            tier=tier,
            permissions=permissions,
            subscription_status=subscription_status,
            subscription_expires=subscription_expires
        )
        
        self.users[person_id] = user
        logger.info(f"User created: {email} (tier: {tier.value})")
        
        return user
    
    def has_permission(self, person_id: str, permission: Permission) -> bool:
        """Check if user has specific permission"""
        
        user = self.users.get(person_id)
        if not user or not user.is_active:
            return False
        
        # Check subscription status for paid permissions
        if permission not in self.TIER_PERMISSIONS[UserTier.FREE]:
            if user.subscription_status not in ["active", "trial"]:
                return False
            
            # Check if subscription is expired
            if user.subscription_expires and datetime.now() > user.subscription_expires:
                return False
        
        return permission in user.permissions
    
    def upgrade_user(self, person_id: str, new_tier: UserTier) -> bool:
        """Upgrade user to new tier"""
        
        user = self.users.get(person_id)
        if not user:
            return False
        
        # Update tier and permissions
        user.tier = new_tier
        user.permissions = self.TIER_PERMISSIONS.get(new_tier, [])
        user.subscription_status = "active"
        user.subscription_expires = datetime.now() + timedelta(days=30)
        
        logger.info(f"User upgraded: {user.email} to {new_tier.value}")
        return True
    
    def get_tier_pricing(self) -> Dict[str, Dict[str, Any]]:
        """Get pricing information for all tiers"""
        
        return {
            "free": {
                "price": 0,
                "currency": "USD",
                "billing_period": None,
                "features": [
                    "Basic AI chat",
                    "Basic personality analysis", 
                    "Community access"
                ]
            },
            "premium": {
                "price": 29.00,
                "currency": "USD",
                "billing_period": "monthly",
                "features": [
                    "Advanced personality analysis",
                    "Basic Schaubilder access",
                    "Voice message analysis",
                    "Premium community groups",
                    "Fourth Way agent access"
                ]
            },
            "pro": {
                "price": 99.00,
                "currency": "USD",
                "billing_period": "monthly",
                "features": [
                    "Full Schaubilder library",
                    "All teaching materials",
                    "Video analysis", 
                    "Custom personality reports",
                    "Master community access",
                    "Multiple specialized agents"
                ]
            },
            "master": {
                "price": 297.00,
                "currency": "USD",
                "billing_period": "monthly",
                "features": [
                    "Complete IP access",
                    "Master prompts access",
                    "Practitioner tools",
                    "Mentorship access", 
                    "All specialized agents",
                    "Priority support"
                ]
            }
        }


async def demo_rbac_system():
    """Demonstrate the RBAC system functionality"""
    
    logger.info("🚀 Starting RBAC System Demo...")
    
    # Initialize RBAC system
    rbac = SimpleRBAC()
    
    # Create test users at different tiers
    free_user = rbac.create_user("free@test.com", "Free User", UserTier.FREE)
    premium_user = rbac.create_user("premium@test.com", "Premium User", UserTier.PREMIUM)
    pro_user = rbac.create_user("pro@test.com", "Pro User", UserTier.PRO)
    master_user = rbac.create_user("master@test.com", "Master User", UserTier.MASTER)
    
    # Test permissions for different users
    logger.info("\n📋 Permission Testing:")
    
    test_permissions = [
        Permission.BASIC_CHAT,
        Permission.ACCESS_SCHAUBILDER_BASIC,
        Permission.ACCESS_SCHAUBILDER_ADVANCED,
        Permission.ACCESS_MASTER_PROMPTS,
        Permission.PRACTITIONER_TOOLS
    ]
    
    users_to_test = [
        ("Free User", free_user),
        ("Premium User", premium_user), 
        ("Pro User", pro_user),
        ("Master User", master_user)
    ]
    
    for user_name, user in users_to_test:
        logger.info(f"\n{user_name} ({user.tier.value}) permissions:")
        for permission in test_permissions:
            has_perm = rbac.has_permission(user.person_id, permission)
            status = "✅" if has_perm else "❌"
            logger.info(f"  {status} {permission.value}")
    
    # Test tier upgrade
    logger.info(f"\n🔄 Testing tier upgrade...")
    logger.info(f"Upgrading {free_user.name} from FREE to PRO")
    
    success = rbac.upgrade_user(free_user.person_id, UserTier.PRO)
    if success:
        logger.info("✅ Upgrade successful!")
        logger.info(f"New permissions for {free_user.name}:")
        for permission in test_permissions:
            has_perm = rbac.has_permission(free_user.person_id, permission)
            status = "✅" if has_perm else "❌"
            logger.info(f"  {status} {permission.value}")
    
    # Display pricing structure
    pricing = rbac.get_tier_pricing()
    logger.info("\n💰 Tier Pricing Structure:")
    for tier, details in pricing.items():
        price_str = f"${details['price']:.2f}" if details['price'] > 0 else "Free"
        period = f"/{details['billing_period']}" if details.get('billing_period') else ""
        logger.info(f"\n📦 {tier.title()}: {price_str}{period}")
        for feature in details['features']:
            logger.info(f"  • {feature}")
    
    logger.success("🎉 RBAC Demo completed successfully!")
    
    return True


async def main():
    """Main demo function"""
    
    logger.info("🛡️ Becoming One™ RBAC System Demo")
    logger.info("=" * 50)
    
    success = await demo_rbac_system()
    
    if success:
        logger.info("\n✅ Demo completed successfully!")
        logger.info("📝 Key RBAC Features Demonstrated:")
        logger.info("   • Tier-based permission system")
        logger.info("   • User registration and profiles")
        logger.info("   • Permission checking")
        logger.info("   • Tier upgrades")
        logger.info("   • Pricing structure")
        logger.info("   • Subscription management")
        
        logger.info("\n🔄 Next Steps:")
        logger.info("   1. Integrate with Supabase for persistence")
        logger.info("   2. Add Telegram payment integration")
        logger.info("   3. Implement session management")
        logger.info("   4. Add permission decorators to AI engine")
        
        return True
    else:
        logger.error("❌ Demo failed")
        return False


if __name__ == "__main__":
    # Load environment variables
    load_dotenv()
    
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
