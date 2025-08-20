"""
SACRED LIBRARY TELEGRAM COMMANDS
Access to Hylozoics Sacred Library through Telegram bot
"""

import os
import sys
from pathlib import Path
from typing import Optional, List, Dict, Any
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import json

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from database.operations import SupabaseClient

class SacredLibraryCommands:
    """Telegram commands for Sacred Library access"""
    
    def __init__(self):
        self.db = SupabaseClient()
    
    async def sacred_search(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Search Sacred Library for quotes"""
        try:
            # Get search query from command arguments
            if context.args:
                query = ' '.join(context.args)
            else:
                await update.message.reply_text(
                    "🔍 **Sacred Library Search**\n\n"
                    "Search the Hylozoics Sacred Library for authentic quotes.\n\n"
                    "**Usage:** `/sacred <search term>`\n\n"
                    "**Examples:**\n"
                    "• `/sacred meditation`\n"
                    "• `/sacred consciousness`\n"
                    "• `/sacred kunskap` (Swedish)\n\n"
                    "🏛️ *Zero hallucinations - only authentic quotes*",
                    parse_mode='Markdown'
                )
                return
            
            # Search Sacred Library in Supabase
            result = self.db.client.table('teaching_materials').select(
                'content, title, metadata'
            ).eq(
                'material_type', 'sacred_quote'
            ).ilike(
                'content', f'%{query}%'
            ).limit(5).execute()
            
            if not result.data:
                await update.message.reply_text(
                    f"🔍 No quotes found for '{query}'\n\n"
                    "Try different search terms or check spelling.\n"
                    "Available languages: Swedish (sv), German (de)",
                    parse_mode='Markdown'
                )
                return
            
            # Format response
            response = f"🏛️ **Sacred Library Results for '{query}'**\n\n"
            
            for i, quote in enumerate(result.data):
                lang = quote['metadata'].get('language', 'unknown')
                chapter = quote['metadata'].get('chapter', 'Unknown')
                
                # Truncate long quotes
                content = quote['content']
                if len(content) > 200:
                    content = content[:200] + "..."
                
                response += f"**{i+1}. [{lang.upper()}] {chapter}**\n"
                response += f"💬 {content}\n\n"
            
            response += "🏛️ *Authentic Hylozoics teachings by Henry T. Laurency*\n"
            response += f"🔍 Found {len(result.data)} of many available quotes"
            
            await update.message.reply_text(response, parse_mode='Markdown')
            
        except Exception as e:
            await update.message.reply_text(
                f"❌ Sacred Library search error: {str(e)}\n\n"
                "Please try again or contact support.",
                parse_mode='Markdown'
            )
    
    async def sacred_browse(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Browse Sacred Library by language or book"""
        try:
            # Create language selection keyboard
            keyboard = [
                [
                    InlineKeyboardButton("🇸🇪 Swedish (Svenska)", callback_data="sacred_lang_sv"),
                    InlineKeyboardButton("🇩🇪 German (Deutsch)", callback_data="sacred_lang_de")
                ],
                [
                    InlineKeyboardButton("📚 All Books", callback_data="sacred_books_all"),
                    InlineKeyboardButton("🔍 Search", callback_data="sacred_search_help")
                ]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                "🏛️ **Sacred Library Browser**\n\n"
                "Browse authentic Hylozoics teachings by Henry T. Laurency.\n\n"
                "**Choose your approach:**\n"
                "• Browse by language\n"
                "• Explore all books\n"
                "• Get search help\n\n"
                "🏛️ *Zero hallucinations - only authentic quotes*",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            await update.message.reply_text(
                f"❌ Sacred Library browser error: {str(e)}",
                parse_mode='Markdown'
            )
    
    async def handle_sacred_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle Sacred Library callback queries"""
        query = update.callback_query
        await query.answer()
        
        try:
            if query.data == "sacred_lang_sv":
                await self._show_language_quotes(query, "sv", "🇸🇪 Swedish")
            elif query.data == "sacred_lang_de":
                await self._show_language_quotes(query, "de", "🇩🇪 German")
            elif query.data == "sacred_books_all":
                await self._show_all_books(query)
            elif query.data == "sacred_search_help":
                await self._show_search_help(query)
                
        except Exception as e:
            await query.edit_message_text(
                f"❌ Sacred Library error: {str(e)}",
                parse_mode='Markdown'
            )
    
    async def _show_language_quotes(self, query, language: str, language_name: str):
        """Show quotes for specific language"""
        result = self.db.client.table('teaching_materials').select(
            'content, title, metadata'
        ).eq(
            'material_type', 'sacred_quote'
        ).eq(
            'metadata->>language', language
        ).limit(3).execute()
        
        if not result.data:
            await query.edit_message_text(
                f"❌ No quotes found for {language_name}",
                parse_mode='Markdown'
            )
            return
        
        response = f"🏛️ **{language_name} Sacred Library**\n\n"
        
        for i, quote in enumerate(result.data):
            chapter = quote['metadata'].get('chapter', 'Unknown')
            content = quote['content']
            if len(content) > 150:
                content = content[:150] + "..."
            
            response += f"**{i+1}. {chapter}**\n"
            response += f"💬 {content}\n\n"
        
        response += f"🏛️ *Showing 3 of many {language_name} quotes*\n"
        response += "Use `/sacred <term>` to search for specific topics"
        
        await query.edit_message_text(response, parse_mode='Markdown')
    
    async def _show_all_books(self, query):
        """Show available books/chapters"""
        result = self.db.client.table('teaching_materials').select(
            'metadata'
        ).eq(
            'material_type', 'sacred_quote'
        ).limit(50).execute()
        
        chapters = set()
        languages = set()
        
        for record in result.data:
            if 'chapter' in record['metadata']:
                chapters.add(record['metadata']['chapter'])
            if 'language' in record['metadata']:
                languages.add(record['metadata']['language'])
        
        response = "📚 **Sacred Library Collection**\n\n"
        response += f"🌐 **Languages:** {', '.join(sorted(languages))}\n\n"
        response += f"📖 **Available Books/Chapters:**\n"
        
        for chapter in sorted(list(chapters))[:10]:  # Show first 10
            response += f"• {chapter}\n"
        
        if len(chapters) > 10:
            response += f"• ... and {len(chapters) - 10} more\n"
        
        response += "\n🔍 Use `/sacred <term>` to search specific content"
        
        await query.edit_message_text(response, parse_mode='Markdown')
    
    async def _show_search_help(self, query):
        """Show search help"""
        response = "🔍 **Sacred Library Search Guide**\n\n"
        response += "**How to search:**\n"
        response += "• `/sacred meditation` - Find quotes about meditation\n"
        response += "• `/sacred consciousness` - Search consciousness topics\n"
        response += "• `/sacred kunskap` - Swedish for 'knowledge'\n\n"
        response += "**Available content:**\n"
        response += "• 4,871 authentic quotes\n"
        response += "• Swedish and German languages\n"
        response += "• Multiple Hylozoics books\n\n"
        response += "🏛️ *All quotes are verbatim from Henry T. Laurency*"
        
        await query.edit_message_text(response, parse_mode='Markdown')

# Initialize commands instance
sacred_commands = SacredLibraryCommands()

# Export command handlers
async def sacred_search_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for /sacred command"""
    await sacred_commands.sacred_search(update, context)

async def sacred_browse_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for /browse_sacred command"""
    await sacred_commands.sacred_browse(update, context)

async def sacred_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for Sacred Library callbacks"""
    await sacred_commands.handle_sacred_callback(update, context)
