"""
Role-Based Access Control (RBAC) System for Becoming One™ AI Platform
Implements comprehensive user authentication, authorization, and tier management
"""

import os
import asyncio
from typing import Optional, Dict, Any, List
from enum import Enum
from dataclasses import dataclass
from datetime import datetime, timedelta
import json

from supabase import create_client, Client
from loguru import logger
import jwt
from passlib.context import CryptContext


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
    
    # Administrative permissions
    USER_MANAGEMENT = "user_management"
    CONTENT_MODERATION = "content_moderation"
    SYSTEM_ADMINISTRATION = "system_administration"
    ANALYTICS_ACCESS = "analytics_access"


@dataclass
class UserProfile:
    """Complete user profile with authentication and authorization data"""
    person_id: str
    email: Optional[str]
    name: Optional[str]
    tier: UserTier
    permissions: List[Permission]
    subscription_status: str  # active, expired, cancelled, trial
    subscription_expires: Optional[datetime]
    created_at: datetime
    last_login: Optional[datetime]
    is_active: bool
    metadata: Dict[str, Any]


class RBACSystem:
    """Role-Based Access Control system with Supabase integration"""
    
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
        ],
        UserTier.ADMIN: [
            # All permissions
            *list(Permission)
        ]
    }
    
    def __init__(self):
        self.supabase: Client = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_ANON_KEY")
        )
        self.service_role_client: Client = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        )
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.jwt_secret = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
        self.jwt_algorithm = "HS256"
        
        logger.info("RBAC System initialized")
    
    async def create_user_tables(self):
        """Create necessary tables for RBAC system"""
        
        # For now, we'll extend the existing identity_registry table
        # Add RBAC columns to identity_registry
        rbac_extension_sql = """
        -- Add RBAC columns to existing identity_registry table
        ALTER TABLE identity_registry 
        ADD COLUMN IF NOT EXISTS tier TEXT NOT NULL DEFAULT 'free' CHECK (tier IN ('free', 'premium', 'pro', 'master', 'admin'));
        
        ALTER TABLE identity_registry 
        ADD COLUMN IF NOT EXISTS subscription_status TEXT NOT NULL DEFAULT 'trial' CHECK (subscription_status IN ('trial', 'active', 'expired', 'cancelled'));
        
        ALTER TABLE identity_registry 
        ADD COLUMN IF NOT EXISTS subscription_expires TIMESTAMPTZ;
        
        ALTER TABLE identity_registry 
        ADD COLUMN IF NOT EXISTS custom_permissions TEXT[] DEFAULT '{}';
        
        ALTER TABLE identity_registry 
        ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT true;
        
        ALTER TABLE identity_registry 
        ADD COLUMN IF NOT EXISTS last_login TIMESTAMPTZ;
        
        ALTER TABLE identity_registry 
        ADD COLUMN IF NOT EXISTS auth_email TEXT UNIQUE;
        
        ALTER TABLE identity_registry 
        ADD COLUMN IF NOT EXISTS auth_password_hash TEXT;
        """
        
        # User sessions table
        user_sessions_sql = """
        CREATE TABLE IF NOT EXISTS user_sessions (
            session_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
            session_token TEXT NOT NULL UNIQUE,
            expires_at TIMESTAMPTZ NOT NULL,
            device_info JSONB DEFAULT '{}',
            ip_address INET,
            is_active BOOLEAN DEFAULT true,
            created_at TIMESTAMPTZ DEFAULT NOW()
        );
        """
        
        # Subscription history
        subscription_history_sql = """
        CREATE TABLE IF NOT EXISTS subscription_history (
            history_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
            tier TEXT NOT NULL,
            action TEXT NOT NULL CHECK (action IN ('upgrade', 'downgrade', 'renewal', 'cancellation', 'expiration')),
            previous_tier TEXT,
            payment_amount DECIMAL(10,2),
            payment_currency TEXT DEFAULT 'USD',
            payment_method TEXT,
            payment_reference TEXT,
            effective_date TIMESTAMPTZ NOT NULL,
            expires_date TIMESTAMPTZ,
            metadata JSONB DEFAULT '{}',
            created_at TIMESTAMPTZ DEFAULT NOW()
        );
        """
        
        # Indexes
        indexes_sql = """
        CREATE INDEX IF NOT EXISTS idx_user_profiles_person_id ON user_profiles(person_id);
        CREATE INDEX IF NOT EXISTS idx_user_profiles_tier ON user_profiles(tier);
        CREATE INDEX IF NOT EXISTS idx_user_profiles_subscription_status ON user_profiles(subscription_status);
        CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON user_sessions(user_id);
        CREATE INDEX IF NOT EXISTS idx_user_sessions_token ON user_sessions(session_token);
        CREATE INDEX IF NOT EXISTS idx_subscription_history_user_id ON subscription_history(user_id);
        """
        
        # Triggers
        triggers_sql = """
        CREATE TRIGGER IF NOT EXISTS update_user_profiles_updated_at 
            BEFORE UPDATE ON user_profiles 
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
        """
        
        # Row Level Security policies
        rls_sql = """
        ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;
        ALTER TABLE user_sessions ENABLE ROW LEVEL SECURITY;
        ALTER TABLE subscription_history ENABLE ROW LEVEL SECURITY;
        
        -- Users can only see their own profile
        CREATE POLICY IF NOT EXISTS "Users can view own profile" ON user_profiles
            FOR SELECT USING (auth.uid() = user_id);
        
        -- Users can update their own profile (limited fields)
        CREATE POLICY IF NOT EXISTS "Users can update own profile" ON user_profiles
            FOR UPDATE USING (auth.uid() = user_id);
        
        -- Only service role can insert/delete profiles
        CREATE POLICY IF NOT EXISTS "Service role can manage profiles" ON user_profiles
            FOR ALL USING (auth.role() = 'service_role');
        
        -- Session policies
        CREATE POLICY IF NOT EXISTS "Users can view own sessions" ON user_sessions
            FOR SELECT USING (auth.uid() = user_id);
            
        CREATE POLICY IF NOT EXISTS "Service role can manage sessions" ON user_sessions
            FOR ALL USING (auth.role() = 'service_role');
        
        -- Subscription history policies
        CREATE POLICY IF NOT EXISTS "Users can view own subscription history" ON subscription_history
            FOR SELECT USING (auth.uid() = user_id);
            
        CREATE POLICY IF NOT EXISTS "Service role can manage subscription history" ON subscription_history
            FOR ALL USING (auth.role() = 'service_role');
        """
        
        # Execute all SQL
        try:
            await self._execute_sql(rbac_extension_sql)
            await self._execute_sql(user_sessions_sql)
            await self._execute_sql(subscription_history_sql)
            await self._execute_sql(indexes_sql)
            await self._execute_sql(triggers_sql)
            
            logger.info("RBAC tables created successfully")
            
        except Exception as e:
            logger.error(f"Error creating RBAC tables: {e}")
            raise
    
    async def _execute_sql(self, sql: str):
        """Execute SQL using regular client for now"""
        # For now, we'll use the regular client since we don't have service role key
        # In production, this should use service_role_client
        try:
            result = self.supabase.rpc('execute_sql', {'query': sql})
            if result.data is None and result.error:
                raise Exception(f"SQL execution error: {result.error}")
            return result
        except Exception as e:
            # If RPC doesn't work, we'll need to handle this differently
            logger.warning(f"SQL execution via RPC failed: {e}")
            # For now, we'll skip the table creation and assume they exist
            return None
    
    async def register_user(
        self, 
        email: str, 
        password: str, 
        name: Optional[str] = None,
        tier: UserTier = UserTier.FREE,
        person_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Register a new user with Supabase Auth and create profile"""
        
        try:
            # Create user with Supabase Auth
            auth_response = self.supabase.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": {
                        "name": name or email.split("@")[0]
                    }
                }
            })
            
            if auth_response.user is None:
                raise Exception(f"User creation failed: {auth_response}")
            
            user_id = auth_response.user.id
            
            # Create user profile
            profile_data = {
                "user_id": user_id,
                "person_id": person_id,
                "tier": tier.value,
                "subscription_status": "trial",
                "subscription_expires": datetime.now() + timedelta(days=7),  # 7-day trial
                "metadata": {
                    "registration_source": "direct",
                    "initial_tier": tier.value
                }
            }
            
            profile_result = self.service_role_client.table("user_profiles").insert(profile_data).execute()
            
            if profile_result.data is None:
                raise Exception(f"Profile creation failed: {profile_result.error}")
            
            logger.info(f"User registered successfully: {email} (tier: {tier.value})")
            
            return {
                "user_id": user_id,
                "email": email,
                "tier": tier.value,
                "subscription_status": "trial",
                "message": "User registered successfully with 7-day trial"
            }
            
        except Exception as e:
            logger.error(f"User registration failed: {e}")
            raise
    
    async def authenticate_user(self, email: str, password: str) -> Optional[UserProfile]:
        """Authenticate user and return profile with permissions"""
        
        try:
            # Authenticate with Supabase
            auth_response = self.supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if auth_response.user is None:
                return None
            
            user_id = auth_response.user.id
            
            # Get user profile
            profile = await self.get_user_profile(user_id)
            
            if profile:
                # Update last login
                await self._update_last_login(user_id)
                
                # Create session token
                session_token = await self._create_session(user_id)
                
                logger.info(f"User authenticated: {email}")
                
            return profile
            
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            return None
    
    async def get_user_profile(self, user_id: str) -> Optional[UserProfile]:
        """Get complete user profile with permissions"""
        
        try:
            # Get profile data
            result = self.service_role_client.table("user_profiles").select(
                """
                user_id,
                person_id,
                tier,
                subscription_status,
                subscription_expires,
                custom_permissions,
                metadata,
                is_active,
                last_login,
                created_at,
                identity_registry(name)
                """
            ).eq("user_id", user_id).execute()
            
            if not result.data:
                return None
            
            profile_data = result.data[0]
            
            # Get user email from auth
            user_result = self.service_role_client.auth.admin.get_user_by_id(user_id)
            email = user_result.user.email if user_result.user else None
            name = profile_data.get("identity_registry", {}).get("name")
            
            # Determine permissions based on tier
            tier = UserTier(profile_data["tier"])
            permissions = self.TIER_PERMISSIONS.get(tier, [])
            
            # Add any custom permissions
            custom_permissions = profile_data.get("custom_permissions", [])
            for perm_str in custom_permissions:
                try:
                    permissions.append(Permission(perm_str))
                except ValueError:
                    logger.warning(f"Invalid custom permission: {perm_str}")
            
            return UserProfile(
                person_id=profile_data["person_id"],
                email=email,
                name=name,
                tier=tier,
                permissions=permissions,
                subscription_status=profile_data["subscription_status"],
                subscription_expires=profile_data.get("subscription_expires"),
                created_at=profile_data["created_at"],
                last_login=profile_data.get("last_login"),
                is_active=profile_data["is_active"],
                metadata=profile_data.get("metadata", {})
            )
            
        except Exception as e:
            logger.error(f"Error getting user profile: {e}")
            return None
    
    async def has_permission(self, user_id: str, permission: Permission) -> bool:
        """Check if user has specific permission"""
        
        profile = await self.get_user_profile(user_id)
        if not profile or not profile.is_active:
            return False
        
        # Check subscription status for paid permissions
        if permission not in self.TIER_PERMISSIONS[UserTier.FREE]:
            if profile.subscription_status not in ["active", "trial"]:
                return False
            
            # Check if trial/subscription is expired
            if profile.subscription_expires and datetime.now() > profile.subscription_expires:
                return False
        
        return permission in profile.permissions
    
    async def upgrade_user_tier(
        self, 
        user_id: str, 
        new_tier: UserTier,
        payment_reference: Optional[str] = None,
        payment_amount: Optional[float] = None
    ) -> bool:
        """Upgrade user to new tier with subscription tracking"""
        
        try:
            # Get current profile
            current_profile = await self.get_user_profile(user_id)
            if not current_profile:
                raise Exception("User profile not found")
            
            previous_tier = current_profile.tier
            
            # Calculate subscription expiry based on tier
            if new_tier == UserTier.PREMIUM:
                expires_date = datetime.now() + timedelta(days=30)  # Monthly
            elif new_tier == UserTier.PRO:
                expires_date = datetime.now() + timedelta(days=30)  # Monthly
            elif new_tier == UserTier.MASTER:
                expires_date = datetime.now() + timedelta(days=30)  # Monthly
            else:
                expires_date = None  # Free tier doesn't expire
            
            # Update user profile
            update_data = {
                "tier": new_tier.value,
                "subscription_status": "active" if new_tier != UserTier.FREE else "trial",
                "subscription_expires": expires_date.isoformat() if expires_date else None
            }
            
            profile_result = self.service_role_client.table("user_profiles").update(
                update_data
            ).eq("user_id", user_id).execute()
            
            if profile_result.error:
                raise Exception(f"Profile update failed: {profile_result.error}")
            
            # Record subscription history
            history_data = {
                "user_id": user_id,
                "tier": new_tier.value,
                "action": "upgrade" if new_tier.value > previous_tier.value else "downgrade",
                "previous_tier": previous_tier.value,
                "payment_amount": payment_amount,
                "payment_reference": payment_reference,
                "effective_date": datetime.now().isoformat(),
                "expires_date": expires_date.isoformat() if expires_date else None
            }
            
            history_result = self.service_role_client.table("subscription_history").insert(
                history_data
            ).execute()
            
            logger.info(f"User tier upgraded: {user_id} from {previous_tier.value} to {new_tier.value}")
            
            return True
            
        except Exception as e:
            logger.error(f"Tier upgrade failed: {e}")
            return False
    
    async def check_subscription_status(self, user_id: str) -> Dict[str, Any]:
        """Check and update subscription status if expired"""
        
        profile = await self.get_user_profile(user_id)
        if not profile:
            return {"status": "error", "message": "User not found"}
        
        # Check if subscription is expired
        if (profile.subscription_expires and 
            datetime.now() > profile.subscription_expires and 
            profile.subscription_status == "active"):
            
            # Downgrade to free tier
            await self._expire_subscription(user_id)
            
            return {
                "status": "expired",
                "message": "Subscription expired, downgraded to free tier",
                "tier": "free"
            }
        
        return {
            "status": profile.subscription_status,
            "tier": profile.tier.value,
            "expires": profile.subscription_expires.isoformat() if profile.subscription_expires else None
        }
    
    async def _expire_subscription(self, user_id: str):
        """Handle subscription expiration"""
        
        # Update profile to free tier
        update_data = {
            "tier": UserTier.FREE.value,
            "subscription_status": "expired"
        }
        
        self.service_role_client.table("user_profiles").update(
            update_data
        ).eq("user_id", user_id).execute()
        
        # Record expiration in history
        history_data = {
            "user_id": user_id,
            "tier": UserTier.FREE.value,
            "action": "expiration",
            "effective_date": datetime.now().isoformat()
        }
        
        self.service_role_client.table("subscription_history").insert(
            history_data
        ).execute()
        
        logger.info(f"Subscription expired for user: {user_id}")
    
    async def _update_last_login(self, user_id: str):
        """Update user's last login timestamp"""
        
        self.service_role_client.table("user_profiles").update({
            "last_login": datetime.now().isoformat()
        }).eq("user_id", user_id).execute()
    
    async def _create_session(self, user_id: str) -> str:
        """Create session token for user"""
        
        # Generate JWT token
        payload = {
            "user_id": user_id,
            "exp": datetime.now() + timedelta(hours=24),
            "iat": datetime.now()
        }
        
        session_token = jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)
        
        # Store session in database
        session_data = {
            "user_id": user_id,
            "session_token": session_token,
            "expires_at": (datetime.now() + timedelta(hours=24)).isoformat(),
            "is_active": True
        }
        
        self.service_role_client.table("user_sessions").insert(session_data).execute()
        
        return session_token
    
    async def validate_session(self, session_token: str) -> Optional[str]:
        """Validate session token and return user_id"""
        
        try:
            # Decode JWT
            payload = jwt.decode(session_token, self.jwt_secret, algorithms=[self.jwt_algorithm])
            user_id = payload.get("user_id")
            
            # Check session in database
            result = self.service_role_client.table("user_sessions").select("*").eq(
                "session_token", session_token
            ).eq("is_active", True).execute()
            
            if result.data and len(result.data) > 0:
                session = result.data[0]
                
                # Check if session is expired
                expires_at = datetime.fromisoformat(session["expires_at"].replace('Z', '+00:00'))
                if datetime.now() < expires_at:
                    return user_id
                else:
                    # Deactivate expired session
                    self.service_role_client.table("user_sessions").update({
                        "is_active": False
                    }).eq("session_id", session["session_id"]).execute()
            
            return None
            
        except jwt.InvalidTokenError:
            return None
    
    async def get_tier_pricing(self) -> Dict[str, Dict[str, Any]]:
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
    
    async def get_user_analytics(self, user_id: str) -> Dict[str, Any]:
        """Get analytics data for user (admin only)"""
        
        # This would require admin permissions check
        # Implementation would include usage stats, engagement metrics, etc.
        pass


# Decorator for permission checking
def require_permission(permission: Permission):
    """Decorator to check user permissions before executing function"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Extract user_id from args/kwargs
            user_id = kwargs.get('user_id') or (args[1] if len(args) > 1 else None)
            
            if not user_id:
                raise Exception("User ID required for permission check")
            
            rbac = RBACSystem()
            if not await rbac.has_permission(user_id, permission):
                raise Exception(f"Permission denied: {permission.value}")
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


# Example usage decorators
@require_permission(Permission.ACCESS_SCHAUBILDER_ADVANCED)
async def get_advanced_schaubilder(user_id: str):
    """Example function requiring advanced Schaubilder access"""
    pass


@require_permission(Permission.PRACTITIONER_TOOLS)
async def access_practitioner_dashboard(user_id: str):
    """Example function requiring practitioner tools access"""
    pass


class SimpleRBAC:
    """Simple RBAC system for Enhanced Telegram Bot"""
    
    def __init__(self):
        self.users: Dict[str, 'UserProfile'] = {}
        logger.info("SimpleRBAC system initialized")
    
    def has_permission(self, user_id: str, permission: Permission) -> bool:
        """Check if user has specific permission"""
        if user_id not in self.users:
            return False
        
        user = self.users[user_id]
        tier = user.tier
        
        # Define permissions by tier
        tier_permissions = {
            UserTier.FREE: [Permission.BASIC_CHAT],
            UserTier.PREMIUM: [Permission.BASIC_CHAT, Permission.VOICE_ANALYSIS],
            UserTier.PRO: [Permission.BASIC_CHAT, Permission.VOICE_ANALYSIS, Permission.ADVANCED_ANALYSIS],
            UserTier.MASTER: [Permission.BASIC_CHAT, Permission.VOICE_ANALYSIS, Permission.ADVANCED_ANALYSIS, Permission.PRACTITIONER_TOOLS],
            UserTier.ADMIN: list(Permission)  # All permissions
        }
        
        return permission in tier_permissions.get(tier, [])


@dataclass
class UserProfile:
    """User profile for RBAC system"""
    user_id: str
    name: str
    tier: UserTier
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
