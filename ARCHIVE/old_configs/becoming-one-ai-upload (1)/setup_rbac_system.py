#!/usr/bin/env python3
"""
Setup script for RBAC System
Creates necessary tables and initializes the Role-Based Access Control system
"""

import asyncio
import os
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from dotenv import load_dotenv
from loguru import logger
from src.core.rbac_system import RBACSystem, UserTier


async def setup_rbac_system():
    """Setup the complete RBAC system"""
    
    logger.info("🚀 Starting RBAC System Setup...")
    
    try:
        # Initialize RBAC system
        rbac = RBACSystem()
        
        # Create all necessary tables
        logger.info("📊 Creating RBAC tables...")
        await rbac.create_user_tables()
        
        # Test the system with a sample user
        logger.info("🧪 Testing system with sample user...")
        
        test_email = "test@becomingone.ai"
        test_password = "TestPassword123!"
        
        # Register test user
        try:
            registration_result = await rbac.register_user(
                email=test_email,
                password=test_password,
                name="Test User",
                tier=UserTier.PREMIUM
            )
            logger.info(f"✅ Test user registered: {registration_result}")
            
        except Exception as e:
            if "User already registered" in str(e):
                logger.info("ℹ️ Test user already exists")
            else:
                logger.warning(f"Test user registration issue: {e}")
        
        # Test authentication
        user_profile = await rbac.authenticate_user(test_email, test_password)
        if user_profile:
            logger.info(f"✅ Authentication test passed: {user_profile.email} (tier: {user_profile.tier.value})")
            
            # Test permissions
            from src.core.rbac_system import Permission
            
            basic_chat = await rbac.has_permission(user_profile.person_id, Permission.BASIC_CHAT)
            advanced_schaubilder = await rbac.has_permission(user_profile.person_id, Permission.ACCESS_SCHAUBILDER_ADVANCED)
            
            logger.info(f"✅ Permission tests:")
            logger.info(f"   - Basic chat: {basic_chat}")
            logger.info(f"   - Advanced Schaubilder: {advanced_schaubilder}")
            
        else:
            logger.error("❌ Authentication test failed")
        
        # Display tier pricing
        pricing = await rbac.get_tier_pricing()
        logger.info("💰 Tier Pricing Structure:")
        for tier, details in pricing.items():
            price_str = f"${details['price']:.2f}" if details['price'] > 0 else "Free"
            period = f"/{details['billing_period']}" if details.get('billing_period') else ""
            logger.info(f"   - {tier.title()}: {price_str}{period}")
            
        logger.success("🎉 RBAC System setup completed successfully!")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ RBAC Setup failed: {e}")
        return False


async def main():
    """Main setup function"""
    
    # Load environment variables
    load_dotenv()
    
    # Check required environment variables
    required_vars = [
        "SUPABASE_URL",
        "SUPABASE_ANON_KEY", 
        "SUPABASE_SERVICE_ROLE_KEY"
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        logger.error(f"❌ Missing required environment variables: {missing_vars}")
        return False
    
    # Setup RBAC system
    success = await setup_rbac_system()
    
    if success:
        logger.info("✅ Setup completed! You can now use the RBAC system.")
        logger.info("📝 Next steps:")
        logger.info("   1. Integrate RBAC with your Telegram bot")
        logger.info("   2. Add payment processing for tier upgrades")
        logger.info("   3. Implement permission checks in your AI engine")
        return True
    else:
        logger.error("❌ Setup failed. Please check the logs above.")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
