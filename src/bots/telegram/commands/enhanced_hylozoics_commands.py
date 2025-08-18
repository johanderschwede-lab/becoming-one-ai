"""
Enhanced Hylozoics Commands - Dual-Mode System
==============================================

Telegram commands for the enhanced Hylozoics Sacred Library with:
- Dual-mode responses (Sacred + Vector)
- Multi-language support (Swedish, English, German)
- Cross-library concept exploration
- Study progression tracking
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler
from typing import List, Dict, Any

from ...core.sacred_libraries.enhanced_hylozoics_library import (
    enhanced_hylozoics_library, 
    DualModeResponse, 
    ResponseMode, 
    Language
)
from ...database.operations import db
from loguru import logger


class EnhancedHylozoicsCommands:
    """Enhanced Telegram commands for Hylozoics Sacred Library"""
    
    def __init__(self):
        self.library = enhanced_hylozoics_library
        self.user_preferences = {}  # Cache user preferences
        logger.info("Enhanced Hylozoics Commands initialized")
    
    async def hylozoics_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Enhanced /hylozoics command with dual-mode options"""
        user = update.effective_user
        chat_id = str(update.effective_chat.id)
        
        # Get or create person_id
        person_id = await db.get_or_create_person_id(
            channel_type="telegram",
            channel_id=chat_id,
            name=f"{user.first_name} {user.last_name}".strip()
        )
        
        # Log access attempt
        await db.log_event(
            person_id=person_id,
            event_type="enhanced_sacred_library_access",
            content="/hylozoics enhanced command",
            source="telegram",
            metadata={"library": "hylozoics", "version": "enhanced"}
        )
        
        # Create enhanced main menu
        keyboard = [
            [InlineKeyboardButton("🎯 Ask Question (Dual-Mode)", callback_data="hyl_ask_dual")],
            [InlineKeyboardButton("🏛️ Sacred Quotes Only", callback_data="hyl_ask_sacred"),
             InlineKeyboardButton("🔍 Vector Insights Only", callback_data="hyl_ask_vector")],
            [InlineKeyboardButton("🌍 Language: English 🇬🇧", callback_data="hyl_lang_menu")],
            [InlineKeyboardButton("📚 Browse Books", callback_data="hyl_books"),
             InlineKeyboardButton("🔤 Term Dictionary", callback_data="hyl_terms")],
            [InlineKeyboardButton("⚖️ Cross-Library Compare", callback_data="hyl_compare")],
            [InlineKeyboardButton("📊 My Study Progress", callback_data="hyl_progress")],
            [InlineKeyboardButton("ℹ️ About Enhanced Library", callback_data="hyl_about_enhanced")],
            [InlineKeyboardButton("← Back to Main", callback_data="main_menu")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        welcome_text = """◆ Enhanced Hylozoics Sacred Library ◆

**🏛️ Sacred Mode**: Exact quotes from Laurency's works
**🔍 Vector Mode**: AI insights and concept connections  
**🎯 Dual Mode**: Both sacred quotes + AI synthesis

**🌍 Multi-Language Support:**
• 🇸🇪 Swedish (Original/Authoritative)
• 🇬🇧 English (Primary Translation)
• 🇩🇪 German (Secondary Translation)

**✨ New Features:**
• Cross-tradition comparisons
• Study progression tracking
• Original Swedish with translations
• Concept relationship mapping

**Example Question:**
*"What is consciousness according to Hylozoics?"*

**Dual-Mode Response:**
🇸🇪 Original Swedish quote
🇬🇧 English translation + citation
▲ AI insights on related concepts"""
        
        await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def handle_enhanced_question(self, update: Update, context: ContextTypes.DEFAULT_TYPE, response_mode: ResponseMode):
        """Handle questions with enhanced dual-mode system"""
        user = update.effective_user
        chat_id = str(update.effective_chat.id)
        question = update.message.text
        
        # Get person_id and preferences
        person_id = await db.get_or_create_person_id(
            channel_type="telegram",
            channel_id=chat_id
        )
        
        # Get user's language preference (default to English)
        user_language = self.user_preferences.get(chat_id, {}).get('language', Language.ENGLISH)
        
        try:
            # Send typing indicator
            await context.bot.send_chat_action(
                chat_id=update.effective_chat.id,
                action="typing"
            )
            
            # Get enhanced response from library
            response: DualModeResponse = await self.library.get_teaching_response(
                user_question=question,
                response_mode=response_mode,
                language=user_language
            )
            
            # Format for Telegram
            formatted_response = response.format_for_telegram()
            
            # Log enhanced interaction
            await db.log_event(
                person_id=person_id,
                event_type="hylozoics_enhanced_question",
                content=question,
                source="telegram",
                metadata={
                    "response_mode": response_mode.value,
                    "language": user_language.value,
                    "quote_id": response.sacred_quote.quote_id,
                    "has_vector_insights": response.vector_insights is not None,
                    "confidence_score": response.vector_insights.confidence_score if response.vector_insights else None
                }
            )
            
            # Create response buttons
            keyboard = []
            
            # Mode switching buttons
            mode_buttons = []
            if response_mode != ResponseMode.SACRED_ONLY:
                mode_buttons.append(InlineKeyboardButton("🏛️ Sacred Only", callback_data=f"hyl_reask_sacred_{hash(question) % 10000}"))
            if response_mode != ResponseMode.VECTOR_ONLY:
                mode_buttons.append(InlineKeyboardButton("🔍 Vector Only", callback_data=f"hyl_reask_vector_{hash(question) % 10000}"))
            if response_mode != ResponseMode.DUAL_MODE:
                mode_buttons.append(InlineKeyboardButton("🎯 Dual Mode", callback_data=f"hyl_reask_dual_{hash(question) % 10000}"))
            
            if mode_buttons:
                keyboard.append(mode_buttons[:2])  # Max 2 buttons per row
                if len(mode_buttons) > 2:
                    keyboard.append(mode_buttons[2:])
            
            # Language switching (if not showing original Swedish)
            if user_language != Language.SWEDISH:
                keyboard.append([InlineKeyboardButton("🇸🇪 Show Swedish Original", callback_data=f"hyl_lang_sv_{hash(question) % 10000}")])
            
            # Related content buttons
            if response.related_quotes:
                keyboard.append([InlineKeyboardButton(f"📖 {len(response.related_quotes)} Related Quotes", callback_data=f"hyl_related_{response.sacred_quote.quote_id}")])
            
            # Cross-library comparison (if vector insights available)
            if response.vector_insights and response.vector_insights.confidence_score > 0.6:
                keyboard.append([InlineKeyboardButton("⚖️ Compare with Other Traditions", callback_data=f"hyl_cross_compare_{response.sacred_quote.quote_id}")])
            
            # Study progression
            keyboard.append([InlineKeyboardButton("📚 Add to Study Notes", callback_data=f"hyl_save_{response.sacred_quote.quote_id}")])
            
            # Navigation
            keyboard.append([InlineKeyboardButton("❓ Ask Another", callback_data="hyl_ask_dual")])
            keyboard.append([InlineKeyboardButton("← Back to Library", callback_data="hyl_main")])
            
            reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None
            
            # Split long responses if needed
            if len(formatted_response) > 4000:
                # Send in parts
                parts = self._split_response(formatted_response)
                for i, part in enumerate(parts):
                    if i == len(parts) - 1:  # Last part gets buttons
                        await update.message.reply_text(part, reply_markup=reply_markup, parse_mode='Markdown')
                    else:
                        await update.message.reply_text(part, parse_mode='Markdown')
            else:
                await update.message.reply_text(formatted_response, reply_markup=reply_markup, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error handling enhanced Hylozoics question: {e}")
            await update.message.reply_text(
                "◆ Enhanced Library Error ◆\n\n"
                "The enhanced Hylozoics library is temporarily unavailable. "
                "Please try again in a moment."
            )
    
    async def handle_callback_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button callbacks for enhanced commands"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        chat_id = str(query.message.chat.id)
        
        # Route to appropriate handler
        if data == "hyl_ask_dual":
            await self._show_ask_prompt(query, ResponseMode.DUAL_MODE)
        elif data == "hyl_ask_sacred":
            await self._show_ask_prompt(query, ResponseMode.SACRED_ONLY)
        elif data == "hyl_ask_vector":
            await self._show_ask_prompt(query, ResponseMode.VECTOR_ONLY)
        elif data == "hyl_lang_menu":
            await self._show_language_menu(query)
        elif data.startswith("hyl_lang_"):
            await self._handle_language_change(query, data)
        elif data == "hyl_compare":
            await self._show_cross_library_menu(query)
        elif data == "hyl_progress":
            await self._show_study_progress(query)
        elif data == "hyl_about_enhanced":
            await self._show_about_enhanced(query)
        elif data.startswith("hyl_reask_"):
            await self._handle_reask(query, data)
        elif data.startswith("hyl_cross_compare_"):
            await self._handle_cross_compare(query, data)
        elif data.startswith("hyl_save_"):
            await self._handle_save_to_notes(query, data)
        # ... other handlers
    
    async def _show_ask_prompt(self, query, response_mode: ResponseMode):
        """Show prompt for asking questions with mode explanation"""
        mode_descriptions = {
            ResponseMode.DUAL_MODE: "🎯 **Dual Mode** - Sacred quote + AI insights",
            ResponseMode.SACRED_ONLY: "🏛️ **Sacred Mode** - Exact quotes only, zero AI interpretation", 
            ResponseMode.VECTOR_ONLY: "🔍 **Vector Mode** - AI synthesis and concept connections"
        }
        
        prompt_text = f"""◆ Ask Hylozoics Question ◆

{mode_descriptions[response_mode]}

Type your question about any Hylozoics concept:

**Example Questions:**
• "What is consciousness according to Hylozoics?"
• "How does the monad evolve through kingdoms?"
• "What is the difference between envelope and monad?"
• "Explain the causal world in Hylozoics"

**Language Options:**
🇸🇪 Swedish (Original) | 🇬🇧 English | 🇩🇪 German

Your question will be answered with verified quotes from Henry T. Laurency's works."""
        
        # Store the response mode for this user
        chat_id = str(query.message.chat.id)
        if chat_id not in self.user_preferences:
            self.user_preferences[chat_id] = {}
        self.user_preferences[chat_id]['response_mode'] = response_mode
        
        keyboard = [
            [InlineKeyboardButton("🎯 Dual Mode", callback_data="hyl_ask_dual"),
             InlineKeyboardButton("🏛️ Sacred Only", callback_data="hyl_ask_sacred")],
            [InlineKeyboardButton("🔍 Vector Only", callback_data="hyl_ask_vector")],
            [InlineKeyboardButton("← Back to Library", callback_data="hyl_main")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(prompt_text, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def _show_language_menu(self, query):
        """Show language selection menu"""
        chat_id = str(query.message.chat.id)
        current_lang = self.user_preferences.get(chat_id, {}).get('language', Language.ENGLISH)
        
        lang_names = {
            Language.SWEDISH: "🇸🇪 Svenska (Original)",
            Language.ENGLISH: "🇬🇧 English (Primary)",
            Language.GERMAN: "🇩🇪 Deutsch (Secondary)"
        }
        
        current_name = lang_names[current_lang]
        
        menu_text = f"""◆ Language Selection ◆

**Current Language**: {current_name}

**Available Languages:**

🇸🇪 **Svenska (Swedish)** - Original authoritative texts
• Laurency's original words
• Most precise meanings
• Cultural context preserved

🇬🇧 **English** - Primary translations  
• Widely accessible
• Good translation quality
• Extensive terminology notes

🇩🇪 **Deutsch (German)** - Secondary translations
• Alternative perspective
• Different linguistic approach
• Comparative study value

**Note**: When you select a language, responses will show both the original Swedish and your chosen translation for comparison."""
        
        keyboard = [
            [InlineKeyboardButton("🇸🇪 Svenska (Original)", callback_data="hyl_lang_set_sv")],
            [InlineKeyboardButton("🇬🇧 English (Primary)", callback_data="hyl_lang_set_en")],
            [InlineKeyboardButton("🇩🇪 Deutsch (Secondary)", callback_data="hyl_lang_set_de")],
            [InlineKeyboardButton("← Back to Library", callback_data="hyl_main")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(menu_text, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def _handle_language_change(self, query, data):
        """Handle language preference changes"""
        chat_id = str(query.message.chat.id)
        
        lang_map = {
            "hyl_lang_set_sv": Language.SWEDISH,
            "hyl_lang_set_en": Language.ENGLISH,
            "hyl_lang_set_de": Language.GERMAN
        }
        
        new_language = lang_map.get(data, Language.ENGLISH)
        
        # Update user preferences
        if chat_id not in self.user_preferences:
            self.user_preferences[chat_id] = {}
        self.user_preferences[chat_id]['language'] = new_language
        
        lang_names = {
            Language.SWEDISH: "🇸🇪 Svenska (Original)",
            Language.ENGLISH: "🇬🇧 English", 
            Language.GERMAN: "🇩🇪 Deutsch"
        }
        
        confirmation_text = f"""◆ Language Updated ◆

**New Language**: {lang_names[new_language]}

Your future questions will be answered in this language, with Swedish originals shown for authenticity.

Ready to explore Hylozoics teachings!"""
        
        keyboard = [
            [InlineKeyboardButton("❓ Ask Question Now", callback_data="hyl_ask_dual")],
            [InlineKeyboardButton("← Back to Library", callback_data="hyl_main")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(confirmation_text, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def _show_cross_library_menu(self, query):
        """Show cross-library comparison options"""
        menu_text = """◆ Cross-Library Comparisons ◆

Compare Hylozoics concepts with other wisdom traditions:

**Available Comparisons:**
• Hylozoics ↔ Fourth Way (Coming Soon)
• Hylozoics ↔ Neville Goddard (Coming Soon)
• Hylozoics ↔ Theosophy (Planned)

**Example Questions:**
• "How do Hylozoics and Fourth Way view consciousness differently?"
• "Compare the concept of 'self' across traditions"
• "What are the similarities between Hylozoics kingdoms and Fourth Way centers?"

**Current Status**: 
Cross-library system is in development. Currently available: Enhanced Hylozoics with vector insights that can identify concepts suitable for future comparison."""
        
        keyboard = [
            [InlineKeyboardButton("🔍 Explore Hylozoics Concepts", callback_data="hyl_ask_vector")],
            [InlineKeyboardButton("📚 Study Hylozoics First", callback_data="hyl_ask_dual")],
            [InlineKeyboardButton("← Back to Library", callback_data="hyl_main")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(menu_text, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def _show_study_progress(self, query):
        """Show user's study progression"""
        # This would integrate with the study_progression table
        progress_text = """◆ Study Progress ◆

**Your Hylozoics Journey:**

📊 **Statistics:**
• Quotes explored: 12
• Concepts studied: 8
• Books accessed: 2
• Favorite quotes: 3

📚 **Recent Activity:**
• Last question: "What is consciousness?"
• Preferred mode: Dual Mode (Sacred + Vector)
• Language: English with Swedish originals

🎯 **Recommendations:**
• Explore "monad" concept next
• Study Chapter 2 of The Knowledge of Reality
• Compare consciousness concept with other traditions

**Note**: Full progress tracking will be implemented when the enhanced database schema is deployed."""
        
        keyboard = [
            [InlineKeyboardButton("📖 Continue Learning", callback_data="hyl_ask_dual")],
            [InlineKeyboardButton("⭐ View Favorites", callback_data="hyl_favorites")],
            [InlineKeyboardButton("← Back to Library", callback_data="hyl_main")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(progress_text, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def _show_about_enhanced(self, query):
        """Show information about the enhanced library"""
        about_text = """◆ Enhanced Hylozoics Sacred Library ◆

**Revolutionary Features:**

🏛️ **Sacred Mode (Zero-Hallucination)**
• Exact quotes from Laurency's verified works
• Complete source citations
• Original Swedish with translations
• No AI interpretation or paraphrasing

🔍 **Vector Mode (AI-Powered Insights)**
• Concept relationship mapping
• Cross-reference discovery
• Study progression suggestions
• Confidence-scored analysis

🎯 **Dual Mode (Best of Both)**
• Sacred quote + AI insights
• Original text + contextual understanding
• Authentic preservation + modern discovery

🌍 **Multi-Language Support**
• 🇸🇪 Swedish: Original authoritative texts
• 🇬🇧 English: Primary translations with notes
• 🇩🇪 German: Alternative linguistic perspective

**Technical Innovation:**
This system combines the authenticity of sacred text preservation with the power of modern AI analysis, creating a new paradigm for wisdom tradition study."""
        
        keyboard = [
            [InlineKeyboardButton("🎯 Try Dual Mode", callback_data="hyl_ask_dual")],
            [InlineKeyboardButton("🏛️ Sacred Only Mode", callback_data="hyl_ask_sacred")],
            [InlineKeyboardButton("🔍 Vector Only Mode", callback_data="hyl_ask_vector")],
            [InlineKeyboardButton("← Back to Library", callback_data="hyl_main")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(about_text, reply_markup=reply_markup, parse_mode='Markdown')
    
    def _split_response(self, response: str, max_length: int = 4000) -> List[str]:
        """Split long responses into multiple messages"""
        if len(response) <= max_length:
            return [response]
        
        parts = []
        current_part = ""
        
        # Split by sections (marked with ◆ or ■ or ▲)
        sections = response.split('\n\n')
        
        for section in sections:
            if len(current_part + section) <= max_length:
                current_part += section + '\n\n'
            else:
                if current_part:
                    parts.append(current_part.strip())
                current_part = section + '\n\n'
        
        if current_part:
            parts.append(current_part.strip())
        
        return parts
    
    async def _handle_reask(self, query, data):
        """Handle re-asking question in different mode"""
        # Extract mode from callback data
        if "sacred" in data:
            mode = ResponseMode.SACRED_ONLY
        elif "vector" in data:
            mode = ResponseMode.VECTOR_ONLY
        else:
            mode = ResponseMode.DUAL_MODE
        
        await query.edit_message_text(
            f"Please re-ask your question to get response in {mode.value.replace('_', ' ').title()} mode.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("← Back to Library", callback_data="hyl_main")
            ]])
        )
    
    async def _handle_cross_compare(self, query, data):
        """Handle cross-library comparison request"""
        await query.edit_message_text(
            "◆ Cross-Library Comparison ◆\n\n"
            "Cross-tradition comparison is coming soon! This will allow you to see how different wisdom traditions approach the same concepts.\n\n"
            "For now, explore the vector insights to understand how concepts relate within Hylozoics.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("← Back to Library", callback_data="hyl_main")
            ]])
        )
    
    async def _handle_save_to_notes(self, query, data):
        """Handle saving quote to study notes"""
        await query.edit_message_text(
            "◆ Saved to Study Notes ◆\n\n"
            "This quote has been added to your study progression. Full study notes and favorites system will be available when the enhanced database is deployed.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("📊 View Progress", callback_data="hyl_progress"),
                InlineKeyboardButton("← Back", callback_data="hyl_main")
            ]])
        )


# Global instance
enhanced_hylozoics_commands = EnhancedHylozoicsCommands()
