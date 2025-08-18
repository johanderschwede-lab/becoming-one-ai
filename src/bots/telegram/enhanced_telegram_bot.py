"""
Enhanced Telegram Bot for Becoming One™ AI Journey System
Integrates RBAC, Telegram Payments, and Advanced Features
"""

import os
import asyncio
from typing import Optional, Dict, Any
from datetime import datetime
from telegram import (
    Update, Bot, InlineKeyboardButton, InlineKeyboardMarkup, 
    LabeledPrice, PreCheckoutQuery, SuccessfulPayment,
    WebAppInfo, KeyboardButton, ReplyKeyboardMarkup
)
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters, ContextTypes,
    CallbackQueryHandler, PreCheckoutQueryHandler
)
from loguru import logger

from database.operations import db
from core.ai_engine import BecomingOneAI
# Make.com integration removed for now
# from integrations.make_webhooks import MakeWebhookClient
from core.rbac_system import SimpleRBAC, UserTier, Permission
from bots.telegram.commands.sacred_library_commands import sacred_search_handler, sacred_browse_handler, sacred_callback_handler
from bots.telegram.commands.hylozoic_study_commands import (
    enter_hylozoic_study_handler, 
    hylozoic_study_callback_handler,
    process_study_question
)


class EnhancedBecomingOneTelegramBot:
    """Enhanced Telegram bot with RBAC, payments, and advanced features"""
    
    def __init__(self):
        self.token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not self.token:
            raise ValueError("TELEGRAM_BOT_TOKEN must be set")
        
        self.payment_provider_token = os.getenv("TELEGRAM_PAYMENT_PROVIDER_TOKEN")
        
        self.ai_engine = BecomingOneAI()
        # Make.com integration removed for now
        # self.make_client = MakeWebhookClient()
        self.rbac = SimpleRBAC()
        self.application = None
        
        logger.info("Enhanced Telegram Bot initialized with RBAC and payment support")
    
    # ============================================================================
    # COMMAND HANDLERS
    # ============================================================================
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Enhanced /start command with tier information"""
        user = update.effective_user
        chat_id = str(update.effective_chat.id)
        
        # Get or create person_id and user profile
        person_id = await db.get_or_create_person_id(
            channel_type="telegram",
            channel_id=chat_id,
            name=f"{user.first_name} {user.last_name}".strip()
        )
        
        # Create RBAC user if not exists
        user_profile = self.rbac.users.get(person_id)
        if not user_profile:
            user_profile = self.rbac.create_user(
                email=f"telegram_{user.id}@temp.com",
                name=f"{user.first_name} {user.last_name}".strip(),
                tier=UserTier.FREE
            )
            self.rbac.users[person_id] = user_profile
        
        # Log the start event
        await db.log_event(
            person_id=person_id,
            event_type="command",
            content="/start",
            source="telegram",
            metadata={"user_id": user.id, "username": user.username}
        )
        
        # Create welcome message with authentic tone
        welcome_message = f"""
▲ You found your way here ▲

Hi {user.first_name}. We're two humans who've discovered some practical methods for human development that actually work.

■ Your Current Access: {user_profile.tier.value.title()}
■ What's Available:
{self._format_tier_features(user_profile.tier)}

Ready to explore what might be useful for you?
        """.strip()
        
        # Create main menu keyboard
        keyboard = await self._create_main_menu_keyboard(person_id)
        
        await update.message.reply_text(
            welcome_message,
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Enhanced help command with tier-specific information"""
        chat_id = str(update.effective_chat.id)
        person_id = await db.get_or_create_person_id(
            channel_type="telegram",
            channel_id=chat_id
        )
        
        user_profile = self.rbac.users.get(person_id)
        if not user_profile:
            await self.start_command(update, context)
            return
        
        help_text = f"""
■ Practical Commands ■

**Available Commands:**
/start - Main menu
/help - This help message  
/profile - Your current access level
/menu - Quick menu
/upgrade - See access options

**Sacred Library:**
/sacred <term> - Search Hylozoics quotes
/browse_sacred - Browse Sacred Library

**Your Access Level:** {user_profile.tier.value.title()}
**What You Can Use:**
{self._format_tier_features(user_profile.tier)}

**Access Levels:**
● **Free:** Basic methods, pattern recognition
● **Premium ($29/mo):** + Advanced methods, voice analysis
● **Pro ($99/mo):** + Full content library, video analysis  
● **Master ($297/mo):** + Complete access, practitioner tools

Type /upgrade to see more options.

→ **Just chat normally** - We'll suggest methods based on what you share.
        """.strip()
        
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def menu_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show main menu with inline keyboard"""
        chat_id = str(update.effective_chat.id)
        person_id = await db.get_or_create_person_id(
            channel_type="telegram",
            channel_id=chat_id
        )
        
        keyboard = await self._create_main_menu_keyboard(person_id)
        
        await update.message.reply_text(
            "■ Main Menu ■\n\nWhat would you like to try?",
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
    
    async def profile_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Enhanced profile with tier and subscription info"""
        chat_id = str(update.effective_chat.id)
        person_id = await db.get_or_create_person_id(
            channel_type="telegram",
            channel_id=chat_id
        )
        
        # Get database profile
        db_profile = await db.get_user_profile(person_id)
        history_count = len(await db.get_user_history(person_id, limit=1000))
        
        # Get RBAC profile
        user_profile = self.rbac.users.get(person_id)
        if not user_profile:
            await self.start_command(update, context)
            return
        
        # Format subscription info
        subscription_status = "✅ Active" if user_profile.subscription_status == "active" else "⏰ Trial"
        expires_info = ""
        if user_profile.subscription_expires:
            expires_info = f"\\n📅 Expires: {user_profile.subscription_expires.strftime('%Y-%m-%d')}"
        
        profile_text = f"""
◆ Your Current Status ◆

**Basic Info:**
● ID: `{str(person_id)[:8]}...`
● Using since: {db_profile['created_at'][:10] if db_profile else 'Today'}
● Interactions: {history_count}

**Access Level:**
● **Current:** {user_profile.tier.value.title()}
● **Status:** {subscription_status}{expires_info}

**What You Can Access:**
{self._format_tier_features(user_profile.tier)}

**Data & Privacy:**
● Data consent: {'Yes' if db_profile and db_profile['consent'] else 'No'}
● All data encrypted and secure

Want more access? Type /upgrade
        """.strip()
        
        await update.message.reply_text(profile_text, parse_mode='Markdown')
    
    async def upgrade_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show upgrade options with Telegram payments"""
        if not self.payment_provider_token:
            await update.message.reply_text(
                "■ Payment system is being set up. Check back soon."
            )
            return
        
        chat_id = str(update.effective_chat.id)
        person_id = await db.get_or_create_person_id(
            channel_type="telegram",
            channel_id=chat_id
        )
        
        user_profile = self.rbac.users.get(person_id)
        current_tier = user_profile.tier if user_profile else UserTier.FREE
        
        # Create upgrade options keyboard
        keyboard = []
        
        if current_tier == UserTier.FREE:
            keyboard.extend([
                [InlineKeyboardButton("▲ Premium Access - $29/mo", callback_data="upgrade_premium")],
                [InlineKeyboardButton("■ Pro Access - $99/mo", callback_data="upgrade_pro")],
                [InlineKeyboardButton("◆ Master Access - $297/mo", callback_data="upgrade_master")]
            ])
        elif current_tier == UserTier.PREMIUM:
            keyboard.extend([
                [InlineKeyboardButton("■ Pro Access - $99/mo", callback_data="upgrade_pro")],
                [InlineKeyboardButton("◆ Master Access - $297/mo", callback_data="upgrade_master")]
            ])
        elif current_tier == UserTier.PRO:
            keyboard.append([InlineKeyboardButton("◆ Master Access - $297/mo", callback_data="upgrade_master")])
        
        keyboard.append([InlineKeyboardButton("● Compare All Levels", callback_data="compare_tiers")])
        keyboard.append([InlineKeyboardButton("← Back to Menu", callback_data="main_menu")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        upgrade_text = f"""
◆ Access Level Options ◆

**Current Level:** {current_tier.value.title()}

**What's Available:**

▲ **Premium ($29/month)**
• Advanced pattern recognition
• Basic method library access
• Voice message analysis
• Premium community groups
• Specialized content access

■ **Pro ($99/month)**
• Full method library
• All teaching materials
• Video analysis capabilities
• Custom development reports
• Master community access
• Multiple specialized tools

◆ **Master ($297/month)**
• Complete content access
• Master method library
• Practitioner tools
• Direct guidance access
• All specialized tools
• Priority support

What level would be most useful for you?
        """.strip()
        
        await update.message.reply_text(
            upgrade_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    # ============================================================================
    # PAYMENT HANDLERS
    # ============================================================================
    
    async def handle_upgrade_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle upgrade button callbacks"""
        query = update.callback_query
        await query.answer()
        
        chat_id = str(query.message.chat_id)
        person_id = await db.get_or_create_person_id(
            channel_type="telegram",
            channel_id=chat_id
        )
        
        if query.data == "compare_tiers":
            await self._show_tier_comparison(query)
            return
        elif query.data == "main_menu":
            keyboard = await self._create_main_menu_keyboard(person_id)
            await query.edit_message_text(
                "■ Main Menu ■\\n\\nWhat would you like to try?",
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
            return
        
        # Handle tier upgrades
        tier_map = {
            "upgrade_premium": (UserTier.PREMIUM, "Premium", 29.00),
            "upgrade_pro": (UserTier.PRO, "Pro", 99.00),
            "upgrade_master": (UserTier.MASTER, "Master", 297.00)
        }
        
        if query.data in tier_map:
            tier, tier_name, price = tier_map[query.data]
            await self._create_payment_invoice(query, person_id, tier, tier_name, price)
    
    async def _create_payment_invoice(self, query, person_id: str, tier: UserTier, tier_name: str, price: float):
        """Create Telegram payment invoice"""
        try:
            # Create invoice
            title = f"Becoming One™ {tier_name} Subscription"
            description = f"Monthly access to {tier_name} tier features including advanced AI coaching and exclusive content."
            
            prices = [LabeledPrice(f"{tier_name} Monthly", int(price * 100))]  # Price in cents
            
            await query.bot.send_invoice(
                chat_id=query.message.chat_id,
                title=title,
                description=description,
                payload=f"upgrade_{tier.value}_{person_id}",
                provider_token=self.payment_provider_token,
                currency="USD",
                prices=prices,
                photo_url="https://willb.one/images/subscription-image.jpg",  # Add your image
                need_email=True,
                need_shipping_address=False,
                is_flexible=False
            )
            
            await query.edit_message_text(
                f"◆ Payment Invoice Created ◆\\n\\n"
                f"Complete the payment to get {tier_name} access.\\n\\n"
                f"**Amount:** ${price:.2f}/month\\n"
                f"**Access:** Full {tier_name} level\\n\\n"
                f"Payment is secure and processed by Telegram.",
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logger.error(f"Error creating payment invoice: {e}")
            await query.edit_message_text(
                "■ Payment Error ■\\n\\n"
                "There was an issue creating the payment. Please try again or contact support.",
                parse_mode='Markdown'
            )
    
    async def precheckout_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle pre-checkout query"""
        query = update.pre_checkout_query
        
        # Validate the payment
        payload_parts = query.invoice_payload.split("_")
        if len(payload_parts) != 3 or payload_parts[0] != "upgrade":
            await query.answer(ok=False, error_message="Invalid payment data")
            return
        
        tier_value = payload_parts[1]
        person_id = payload_parts[2]
        
        # Validate tier and person
        try:
            tier = UserTier(tier_value)
            # Could add additional validation here
            await query.answer(ok=True)
        except ValueError:
            await query.answer(ok=False, error_message="Invalid subscription tier")
    
    async def successful_payment_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle successful payment"""
        payment: SuccessfulPayment = update.message.successful_payment
        
        # Parse payment payload
        payload_parts = payment.invoice_payload.split("_")
        tier_value = payload_parts[1]
        person_id = payload_parts[2]
        
        try:
            tier = UserTier(tier_value)
            
            # Upgrade user in RBAC system
            success = self.rbac.upgrade_user(person_id, tier)
            
            if success:
                # Log the upgrade
                await db.log_event(
                    person_id=person_id,
                    event_type="tier_upgrade",
                    content=f"Upgraded to {tier.value}",
                    source="telegram",
                    metadata={
                        "payment_id": payment.telegram_payment_charge_id,
                        "amount": payment.total_amount / 100,
                        "currency": payment.currency
                    }
                )
                
                user_profile = self.rbac.users[person_id]
                
                success_message = f"""
▲ Access Upgrade Complete ▲

Welcome to {tier.value.title()} level! Your access is now active.

**What You Can Now Use:**
{self._format_tier_features(tier)}

**Payment Confirmed:**
● Amount: ${payment.total_amount / 100:.2f} {payment.currency.upper()}
● Transaction: `{payment.telegram_payment_charge_id}`

Ready to try your new access? Type /menu to get started.
                """.strip()
                
                await update.message.reply_text(success_message, parse_mode='Markdown')
                
            else:
                await update.message.reply_text(
                    "■ There was an issue processing your upgrade. Please contact support."
                )
                
        except Exception as e:
            logger.error(f"Error processing successful payment: {e}")
            await update.message.reply_text(
                "■ Payment received but upgrade failed. Please contact support."
            )
    
    # ============================================================================
    # MESSAGE HANDLING WITH RBAC
    # ============================================================================
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Enhanced message handling with RBAC permissions"""
        user = update.effective_user
        chat_id = str(update.effective_chat.id)
        message_text = update.message.text
        
        try:
            # Get person_id and user profile
            person_id = await db.get_or_create_person_id(
                channel_type="telegram",
                channel_id=chat_id,
                name=f"{user.first_name} {user.last_name}".strip()
            )
            
            # Check user permissions
            user_profile = self.rbac.users.get(person_id)
            if not user_profile:
                # Create new user
                user_profile = self.rbac.create_user(
                    email=f"telegram_{user.id}@temp.com",
                    name=f"{user.first_name} {user.last_name}".strip(),
                    tier=UserTier.FREE
                )
                self.rbac.users[person_id] = user_profile
            
            # Check basic chat permission
            if not self.rbac.has_permission(person_id, Permission.BASIC_CHAT):
                await update.message.reply_text(
                    "■ Your account doesn't have chat permissions. Please contact support."
                )
                return
            
            # Log the incoming message
            await db.log_event(
                person_id=person_id,
                event_type="message",
                content=message_text,
                source="telegram",
                metadata={
                    "user_id": user.id,
                    "username": user.username,
                    "chat_id": chat_id,
                    "tier": user_profile.tier.value
                }
            )
            
            # Send typing indicator
            await context.bot.send_chat_action(
                chat_id=update.effective_chat.id,
                action="typing"
            )
            
            # Check for voice analysis permission if voice message
            if update.message.voice and not self.rbac.has_permission(person_id, Permission.VOICE_ANALYSIS):
                await update.message.reply_text(
                    "● Voice analysis is available in Premium level and above. Type /upgrade to see options."
                )
                return
            
            # Process with AI engine (with tier context)
            response = await self.ai_engine.process_message(
                person_id=person_id,
                message=message_text,
                source="telegram",
                user_tier=user_profile.tier.value  # Pass tier for personalized responses
            )
            
            # Add tier-specific suggestions
            if user_profile.tier == UserTier.FREE and len(response) > 200:
                response += "\\n\\n→ *Want deeper analysis? Premium level has advanced methods. Type /upgrade*"
            
            # Log the response
            await db.log_event(
                person_id=person_id,
                event_type="response",
                content=response,
                source="telegram",
                metadata={
                    "ai_generated": True,
                    "tier": user_profile.tier.value
                }
            )
            
            # Send response
            await update.message.reply_text(response, parse_mode='Markdown')
            
            # Make.com webhook removed for now
            # await self.make_client.trigger_message_webhook({
            #     "person_id": str(person_id),
            #     "message": message_text,
            #     "response": response,
            #     "source": "telegram",
            #     "tier": user_profile.tier.value,
            #     "user_info": {
            #         "telegram_id": user.id,
            #         "username": user.username,
            #         "name": f"{user.first_name} {user.last_name}".strip()
            #     }
            # })
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            await update.message.reply_text(
                "■ I encountered an issue processing your message. Please try again in a moment."
            )
    
    # ============================================================================
    # UTILITY METHODS
    # ============================================================================
    
    async def _create_main_menu_keyboard(self, person_id: str) -> InlineKeyboardMarkup:
        """Create main menu keyboard based on user permissions"""
        user_profile = self.rbac.users.get(person_id)
        keyboard = []
        
        # Basic features (available to all)
        keyboard.append([InlineKeyboardButton("● Pattern Recognition", callback_data="personality")])
        
        # Premium features
        if user_profile and self.rbac.has_permission(person_id, Permission.ACCESS_SCHAUBILDER_BASIC):
            keyboard.append([InlineKeyboardButton("■ Method Library", callback_data="schaubilder")])
        
        # Pro features
        if user_profile and self.rbac.has_permission(person_id, Permission.ACCESS_TEACHING_MATERIALS):
            keyboard.append([InlineKeyboardButton("▲ Teaching Materials", callback_data="teachings")])
        
        # Master features
        if user_profile and self.rbac.has_permission(person_id, Permission.PRACTITIONER_TOOLS):
            keyboard.append([InlineKeyboardButton("◆ Practitioner Tools", callback_data="tools")])
        
        # Always available
        keyboard.extend([
            [InlineKeyboardButton("○ My Status", callback_data="profile")],
            [InlineKeyboardButton("→ Access Options", callback_data="upgrade")],
            [InlineKeyboardButton("? Help & Support", callback_data="help")]
        ])
        
        return InlineKeyboardMarkup(keyboard)
    
    def _format_tier_features(self, tier: UserTier) -> str:
        """Format tier features for display"""
        permissions = self.rbac.TIER_PERMISSIONS.get(tier, [])
        
        feature_map = {
            Permission.BASIC_CHAT: "● Basic Methods",
            Permission.PERSONALITY_ANALYSIS: "● Pattern Recognition",
            Permission.ACCESS_SCHAUBILDER_BASIC: "■ Basic Method Library",
            Permission.ACCESS_SCHAUBILDER_ADVANCED: "■ Advanced Method Library",
            Permission.ACCESS_TEACHING_MATERIALS: "▲ Teaching Materials",
            Permission.ACCESS_MASTER_PROMPTS: "◆ Master Methods",
            Permission.VOICE_ANALYSIS: "● Voice Analysis",
            Permission.VIDEO_ANALYSIS: "● Video Analysis",
            Permission.CUSTOM_PERSONALITY_REPORTS: "● Custom Reports",
            Permission.PRACTITIONER_TOOLS: "◆ Practitioner Tools",
            Permission.PREMIUM_GROUPS: "→ Premium Community",
            Permission.MASTER_GROUPS: "→ Master Community",
            Permission.MENTORSHIP_ACCESS: "→ Direct Guidance"
        }
        
        features = []
        for permission in permissions:
            if permission in feature_map:
                features.append(f"• {feature_map[permission]}")
        
        return "\\n".join(features) if features else "• Basic methods only"
    
    async def _show_tier_comparison(self, query):
        """Show detailed tier comparison"""
        comparison_text = """
◆ Access Level Comparison ◆

**● FREE**
• Basic methods
• Simple pattern recognition
• Community access

**▲ PREMIUM - $29/month**
• Everything in Free +
• Advanced pattern recognition
• Basic method library access
• Voice message analysis
• Premium community groups
• Specialized content access

**■ PRO - $99/month**
• Everything in Premium +
• Full method library
• All teaching materials
• Video analysis capabilities
• Custom development reports
• Master community access
• Multiple specialized tools

**◆ MASTER - $297/month**
• Everything in Pro +
• Complete content access
• Master method library
• Practitioner tools
• Direct guidance access
• All specialized tools
• Priority support

What level would work best for you?
        """.strip()
        
        keyboard = [
            [InlineKeyboardButton("▲ Choose Premium", callback_data="upgrade_premium")],
            [InlineKeyboardButton("■ Choose Pro", callback_data="upgrade_pro")],
            [InlineKeyboardButton("◆ Choose Master", callback_data="upgrade_master")],
            [InlineKeyboardButton("← Back", callback_data="upgrade")]
        ]
        
        await query.edit_message_text(
            comparison_text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    
    # ============================================================================
    # MESSAGE HANDLING
    # ============================================================================
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle regular messages with study mode and AI responses"""
        user = update.effective_user
        message = update.message.text if update.message.text else ""
        chat_id = update.effective_chat.id
        
        if not message:
            return
        
        try:
            # Check if user is in study mode and awaiting a question
            if context.user_data.get('awaiting_study_question'):
                await process_study_question(update, context)
                return
            
            # Check if user is asking for Hylozoic input
            hylozoic_triggers = ['hylozoic', 'laurency', 'sacred', 'teachings']
            wants_hylozoic = any(trigger in message.lower() for trigger in hylozoic_triggers)
            
            if wants_hylozoic or context.user_data.get('study_mode') == 'hylozoic':
                # Provide Hylozoic-enhanced response
                person_id = uuid.uuid4()  # Temporary
                response = await self.ai_engine.process_message(
                    person_id=person_id,
                    message=message,
                    source="telegram",
                    user_tier="premium"  # You have full access
                )
                
                await update.message.reply_text(response)
            else:
                # Ask if they want Hylozoic perspective
                keyboard = [
                    [
                        InlineKeyboardButton("🏛️ Get Hylozoic View", callback_data=f"add_hylozoic_{hash(message) % 10000}"),
                        InlineKeyboardButton("🎓 Enter Study Room", callback_data="enter_study_room")
                    ]
                ]
                
                # Generate normal response
                person_id = uuid.uuid4()  # Temporary
                response = await self.ai_engine.process_message(
                    person_id=person_id,
                    message=message,
                    source="telegram",
                    user_tier="free"  # Normal mode
                )
                
                await update.message.reply_text(
                    response,
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
                
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            await update.message.reply_text("I'm having trouble processing that. Please try again.")
    
    # ============================================================================
    # SETUP AND RUN
    # ============================================================================
    
    def setup_handlers(self):
        """Set up all bot handlers"""
        # Command handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("menu", self.menu_command))
        self.application.add_handler(CommandHandler("profile", self.profile_command))
        self.application.add_handler(CommandHandler("upgrade", self.upgrade_command))
        
        # Sacred Library commands
        self.application.add_handler(CommandHandler("sacred", sacred_search_handler))
        self.application.add_handler(CommandHandler("browse_sacred", sacred_browse_handler))
        self.application.add_handler(CommandHandler("study", enter_hylozoic_study_handler))
        self.application.add_handler(CommandHandler("hylozoic", enter_hylozoic_study_handler))
        
        # Callback query handlers
        self.application.add_handler(CallbackQueryHandler(self.handle_upgrade_callback))
        self.application.add_handler(CallbackQueryHandler(sacred_callback_handler, pattern="^sacred_"))
        self.application.add_handler(CallbackQueryHandler(hylozoic_study_callback_handler, pattern="^study_"))
        
        # Payment handlers
        self.application.add_handler(PreCheckoutQueryHandler(self.precheckout_callback))
        self.application.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, self.successful_payment_callback))
        
        # General message handler (must be last)
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        self.application.add_handler(
            MessageHandler(filters.VOICE, self.handle_message)
        )
    
    async def run(self):
        """Run the enhanced bot"""
        self.application = Application.builder().token(self.token).build()
        self.setup_handlers()
        
        logger.info("▲ Starting Becoming One™ Telegram Bot with RBAC and Payments...")
        await self.application.run_polling()


if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    bot = EnhancedBecomingOneTelegramBot()
    asyncio.run(bot.run())
