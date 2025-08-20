"""
Hylozoics Sacred Library Commands for Telegram Bot
=================================================

Commands for accessing Henry T. Laurency's teachings through exact quotes only.
Zero-hallucination system with source verification.
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler
from typing import List, Dict, Any

from ...core.sacred_libraries.hylozoics_library import hylozoics_library, HylozoicsResponse
from ...database.operations import db
from loguru import logger


class HylozoicsCommands:
    """Telegram commands for Hylozoics Sacred Library access"""
    
    def __init__(self):
        self.library = hylozoics_library
        logger.info("Hylozoics Commands initialized")
    
    async def hylozoics_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Main /hylozoics command - gateway to Sacred Library"""
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
            event_type="sacred_library_access",
            content="/hylozoics command",
            source="telegram",
            metadata={"library": "hylozoics", "access_type": "main_menu"}
        )
        
        # Create main menu
        keyboard = [
            [InlineKeyboardButton("📖 Ask a Question", callback_data="hyl_ask")],
            [InlineKeyboardButton("📚 Browse Books", callback_data="hyl_books")],
            [InlineKeyboardButton("🔍 Search Terms", callback_data="hyl_terms")],
            [InlineKeyboardButton("ℹ️ About Hylozoics", callback_data="hyl_about")],
            [InlineKeyboardButton("← Back to Main", callback_data="main_menu")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        welcome_text = """◆ Hylozoics Sacred Library ◆

Access to Henry T. Laurency's teachings through exact quotes only.

■ **Zero Hallucination System**
• Only authentic quotes from source texts
• Complete source citations provided
• No interpretations or paraphrasing

▲ **What you can do:**
• Ask questions about Hylozoics concepts
• Browse Laurency's books and chapters
• Search for specific terminology
• Get exact quotes with full context

**Note**: This library contains only verified quotes from Laurency's works. All responses include precise source citations."""
        
        await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def handle_hylozoics_question(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle user questions about Hylozoics"""
        user = update.effective_user
        chat_id = str(update.effective_chat.id)
        question = update.message.text
        
        # Get person_id
        person_id = await db.get_or_create_person_id(
            channel_type="telegram",
            channel_id=chat_id
        )
        
        try:
            # Send typing indicator
            await context.bot.send_chat_action(
                chat_id=update.effective_chat.id,
                action="typing"
            )
            
            # Get response from Sacred Library
            response: HylozoicsResponse = await self.library.get_teaching_response(question)
            
            # Format for Telegram
            formatted_response = response.format_for_telegram()
            
            # Log interaction
            await db.log_event(
                person_id=person_id,
                event_type="hylozoics_question",
                content=question,
                source="telegram",
                metadata={
                    "quote_id": response.exact_quote.quote_id,
                    "source_book": response.exact_quote.source_book,
                    "has_related": len(response.related_quotes) > 0
                }
            )
            
            # Send response with options for related quotes
            keyboard = []
            
            if response.related_quotes:
                keyboard.append([
                    InlineKeyboardButton(
                        f"📖 Show {len(response.related_quotes)} Related Quotes", 
                        callback_data=f"hyl_related_{response.exact_quote.quote_id}"
                    )
                ])
            
            # Add terminology lookup if the response contains Hylozoics terms
            if response.exact_quote.hylozoics_terms:
                keyboard.append([
                    InlineKeyboardButton("🔍 Define Terms", callback_data=f"hyl_define_{response.exact_quote.quote_id}")
                ])
            
            keyboard.append([InlineKeyboardButton("📖 Ask Another Question", callback_data="hyl_ask")])
            keyboard.append([InlineKeyboardButton("← Back to Library", callback_data="hyl_main")])
            
            reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None
            
            await update.message.reply_text(
                formatted_response, 
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logger.error(f"Error handling Hylozoics question: {e}")
            await update.message.reply_text(
                "◆ Sacred Library Error ◆\n\n"
                "The Hylozoics library is temporarily unavailable. "
                "Please try again in a moment."
            )
    
    async def handle_callback_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button callbacks for Hylozoics commands"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        
        if data == "hyl_ask":
            await self._show_ask_prompt(query)
        elif data == "hyl_books":
            await self._show_books_menu(query)
        elif data == "hyl_terms":
            await self._show_terms_menu(query)
        elif data == "hyl_about":
            await self._show_about_hylozoics(query)
        elif data.startswith("hyl_related_"):
            quote_id = data.replace("hyl_related_", "")
            await self._show_related_quotes(query, quote_id)
        elif data.startswith("hyl_define_"):
            quote_id = data.replace("hyl_define_", "")
            await self._show_term_definitions(query, quote_id)
        elif data.startswith("hyl_book_"):
            book_title = data.replace("hyl_book_", "").replace("_", " ")
            await self._show_book_structure(query, book_title)
    
    async def _show_ask_prompt(self, query):
        """Show prompt for asking questions"""
        prompt_text = """◆ Ask Hylozoics Question ◆

Type your question about any Hylozoics concept, and I'll search Henry T. Laurency's works for exact quotes that address your inquiry.

**Examples:**
• "What is consciousness according to Hylozoics?"
• "How does evolution work in the kingdoms?"
• "What is the difference between monad and envelope?"
• "What does Laurency say about causal consciousness?"

**Remember**: Responses will contain only exact quotes from Laurency's works with full source citations."""
        
        keyboard = [[InlineKeyboardButton("← Back to Library", callback_data="hyl_main")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(prompt_text, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def _show_books_menu(self, query):
        """Show available Hylozoics books"""
        books_text = """◆ Hylozoics Books ◆

**Available works by Henry T. Laurency:**

📖 **The Knowledge of Reality** (1979)
• Introduction to Hylozoics
• Basic concepts and terminology
• Difficulty: Intermediate

📖 **The Philosopher's Stone** (1980)
• Advanced consciousness teachings
• Cosmic evolution principles
• Difficulty: Advanced

📖 **The Way of Man** (1981)
• Practical development guidance
• Human evolution pathway
• Difficulty: Intermediate

Select a book to browse its chapters and sections."""
        
        keyboard = [
            [InlineKeyboardButton("📖 The Knowledge of Reality", callback_data="hyl_book_The_Knowledge_of_Reality")],
            [InlineKeyboardButton("📖 The Philosopher's Stone", callback_data="hyl_book_The_Philosophers_Stone")],
            [InlineKeyboardButton("📖 The Way of Man", callback_data="hyl_book_The_Way_of_Man")],
            [InlineKeyboardButton("← Back to Library", callback_data="hyl_main")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(books_text, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def _show_terms_menu(self, query):
        """Show Hylozoics terminology menu"""
        terms_text = """◆ Hylozoics Terminology ◆

**Core Concepts:**

🔹 **Fundamental Terms:**
• Hylozoics - The esoteric knowledge system
• Consciousness - The fundamental property of existence
• Monad - The ultimate unit of consciousness
• Evolution - Development through kingdoms

🔹 **Structural Terms:**
• Envelope - Temporary vehicles of consciousness
• Kingdom - Stages of evolution (mineral, vegetable, animal, human)
• World - Dimensional planes of existence

🔹 **Development Terms:**
• Causal - Abstract thought and wisdom world
• Mental - Concrete thought world  
• Emotional - Feelings and desires world

Type any term to get Laurency's exact definition."""
        
        keyboard = [
            [InlineKeyboardButton("🔍 Search All Terms", callback_data="hyl_search_terms")],
            [InlineKeyboardButton("← Back to Library", callback_data="hyl_main")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(terms_text, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def _show_about_hylozoics(self, query):
        """Show information about Hylozoics"""
        about_text = """◆ About Hylozoics ◆

**Hylozoics** is the esoteric knowledge of life and matter, as presented by **Henry T. Laurency** (1882-1971).

■ **Core Teaching:**
"All existence is conscious" - from the smallest atom to the greatest cosmic being, consciousness is the fundamental property of reality.

■ **Key Principles:**
• Evolution of consciousness through kingdoms
• Seven worlds or planes of existence
• The monad as the ultimate unit of consciousness
• Envelopes as temporary vehicles for development

■ **Sacred Library Approach:**
This system provides only **exact quotes** from Laurency's verified works. No interpretations, no paraphrasing - only the authentic teachings with complete source citations.

■ **Purpose:**
To preserve and share Laurency's teachings in their original form, allowing students to encounter the pure wisdom without modern additions or modifications."""
        
        keyboard = [
            [InlineKeyboardButton("📖 Start Reading", callback_data="hyl_books")],
            [InlineKeyboardButton("❓ Ask a Question", callback_data="hyl_ask")],
            [InlineKeyboardButton("← Back to Library", callback_data="hyl_main")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(about_text, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def _show_related_quotes(self, query, quote_id: str):
        """Show related quotes for a given quote"""
        # This would retrieve and display related quotes
        # Implementation depends on the specific quote_id structure
        await query.edit_message_text(
            "◆ Related Quotes ◆\n\n"
            "Related quote functionality will be implemented when quotes are added to the library.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("← Back to Library", callback_data="hyl_main")
            ]])
        )
    
    async def _show_term_definitions(self, query, quote_id: str):
        """Show definitions for terms in a quote"""
        # This would show definitions for Hylozoics terms
        await query.edit_message_text(
            "◆ Term Definitions ◆\n\n"
            "Term definition functionality will be implemented when the terminology database is populated.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("← Back to Library", callback_data="hyl_main")
            ]])
        )
    
    async def _show_book_structure(self, query, book_title: str):
        """Show the structure of a specific book"""
        try:
            structure = await self.library.get_book_structure(book_title)
            
            if not structure:
                await query.edit_message_text(
                    f"◆ {book_title} ◆\n\n"
                    f"Book structure not yet available. Quotes from {book_title} need to be added to the Sacred Library.",
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("← Back to Books", callback_data="hyl_books")
                    ]])
                )
                return
            
            # Format book structure
            structure_text = f"◆ {book_title} ◆\n\n**Chapters:**\n\n"
            
            for chapter, sections in structure.items():
                structure_text += f"📖 **{chapter}**\n"
                if sections:
                    for section in sections:
                        structure_text += f"  • {section}\n"
                structure_text += "\n"
            
            structure_text += "**Note**: Select a chapter to browse available quotes."
            
            keyboard = [[InlineKeyboardButton("← Back to Books", callback_data="hyl_books")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(structure_text, reply_markup=reply_markup, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error showing book structure: {e}")
            await query.edit_message_text(
                "Error loading book structure.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("← Back to Books", callback_data="hyl_books")
                ]])
            )


# Global instance
hylozoics_commands = HylozoicsCommands()
