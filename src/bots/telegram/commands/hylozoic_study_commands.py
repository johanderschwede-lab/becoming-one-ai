"""
HYLOZOIC STUDY ROOM COMMANDS
Interactive Hylozoic University experience
"""

import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from loguru import logger
import uuid

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from database.operations import db
from core.ai_engine import BecomingOneAI

# Initialize AI engine for study sessions
study_ai = BecomingOneAI()

async def enter_hylozoic_study_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Enter Hylozoic Study Room - focused learning mode"""
    user = update.effective_user
    chat_id = update.effective_chat.id
    
    try:
        # Store study mode in user context
        context.user_data['study_mode'] = 'hylozoic'
        context.user_data['study_session_id'] = str(uuid.uuid4())
        
        welcome_message = """🏛️ **WELCOME TO HYLOZOIC UNIVERSITY**

You've entered a focused study environment for authentic Hylozoics teachings by Henry T. Laurency.

**In this study room:**
▲ All responses include relevant Hylozoic quotes
■ Questions are answered from the Sacred Library  
◆ Deep conceptual exploration is encouraged
● Focus on understanding, not quick answers

**Study Options:**"""

        keyboard = [
            [
                InlineKeyboardButton("📚 Browse Topics", callback_data="study_browse_topics"),
                InlineKeyboardButton("🔍 Ask Question", callback_data="study_ask_question")
            ],
            [
                InlineKeyboardButton("📖 Random Quote", callback_data="study_random_quote"),
                InlineKeyboardButton("🎓 Guided Study", callback_data="study_guided")
            ],
            [
                InlineKeyboardButton("🚪 Exit Study Room", callback_data="study_exit")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            welcome_message,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
        logger.info(f"User {user.id} entered Hylozoic study room")
        
    except Exception as e:
        logger.error(f"Error entering study room: {e}")
        await update.message.reply_text("Unable to enter study room. Please try again.")

async def hylozoic_study_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle study room interactions"""
    query = update.callback_query
    await query.answer()
    
    user = query.from_user
    chat_id = query.message.chat_id
    action = query.data
    
    try:
        if action == "study_browse_topics":
            await handle_browse_topics(query, context)
        elif action == "study_ask_question":
            await handle_ask_question(query, context)
        elif action == "study_random_quote":
            await handle_random_quote(query, context)
        elif action == "study_guided":
            await handle_guided_study(query, context)
        elif action == "study_exit":
            await handle_exit_study(query, context)
        elif action.startswith("study_topic_"):
            topic = action.replace("study_topic_", "")
            await handle_topic_study(query, context, topic)
        
    except Exception as e:
        logger.error(f"Error handling study callback: {e}")
        await query.message.reply_text("Study room error. Please try again.")

async def handle_browse_topics(query, context):
    """Show available study topics"""
    topics_message = """📚 **HYLOZOIC STUDY TOPICS**

Choose a topic for focused study:"""

    keyboard = [
        [
            InlineKeyboardButton("🧘 Consciousness", callback_data="study_topic_consciousness"),
            InlineKeyboardButton("🌱 Development", callback_data="study_topic_development")
        ],
        [
            InlineKeyboardButton("💭 Mind & Thinking", callback_data="study_topic_mind"),
            InlineKeyboardButton("❤️ Love & Emotion", callback_data="study_topic_love")
        ],
        [
            InlineKeyboardButton("🎯 Purpose & Will", callback_data="study_topic_purpose"),
            InlineKeyboardButton("⚡ Energy & Power", callback_data="study_topic_energy")
        ],
        [
            InlineKeyboardButton("🔄 Reincarnation", callback_data="study_topic_reincarnation"),
            InlineKeyboardButton("🌌 Cosmic Order", callback_data="study_topic_cosmic")
        ],
        [
            InlineKeyboardButton("🔙 Back to Study Menu", callback_data="study_main_menu")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        topics_message,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def handle_ask_question(query, context):
    """Prompt user to ask a question"""
    context.user_data['awaiting_study_question'] = True
    
    await query.edit_message_text(
        """🤔 **ASK YOUR HYLOZOIC QUESTION**

Please type your question about Hylozoics, consciousness, development, or any related topic.

I'll search the Sacred Library and provide authentic Laurency teachings to help answer your question.

**Examples:**
• "What is consciousness according to Laurency?"
• "How does reincarnation work in Hylozoics?"
• "What are the stages of human development?"
• "How can I develop my thinking abilities?"

Type your question now...""",
        parse_mode='Markdown'
    )

async def handle_random_quote(query, context):
    """Provide a random Hylozoic quote"""
    try:
        # Get a random quote from Sacred Library
        result = db.client.table('teaching_materials').select(
            'content, title, metadata'
        ).eq(
            'material_type', 'sacred_quote'
        ).limit(1).execute()
        
        if result.data:
            quote = result.data[0]
            content = quote['content']
            chapter = quote['metadata'].get('chapter', 'Unknown')
            language = quote['metadata'].get('language', 'unknown')
            
            quote_message = f"""📜 **RANDOM HYLOZOIC WISDOM**

"{content}"

— Henry T. Laurency, {chapter} ({language.upper()})

🔄 Want another quote? Click the button below."""
            
            keyboard = [
                [
                    InlineKeyboardButton("🎲 Another Quote", callback_data="study_random_quote"),
                    InlineKeyboardButton("💬 Discuss This", callback_data="study_discuss_quote")
                ],
                [
                    InlineKeyboardButton("🔙 Back to Study", callback_data="study_main_menu")
                ]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                quote_message,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        else:
            await query.edit_message_text("Unable to retrieve quote. Please try again.")
            
    except Exception as e:
        logger.error(f"Error getting random quote: {e}")
        await query.edit_message_text("Error retrieving quote. Please try again.")

async def handle_guided_study(query, context):
    """Start guided study session"""
    await query.edit_message_text(
        """🎓 **GUIDED HYLOZOIC STUDY**

Welcome to a structured learning journey through Hylozoics.

**Study Path Options:**

▲ **Beginner Path**: Fundamental concepts and worldview
■ **Intermediate Path**: Consciousness and development  
◆ **Advanced Path**: Cosmic order and higher principles
● **Custom Path**: Choose your own focus areas

Which path interests you most?""",
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton("▲ Beginner", callback_data="study_path_beginner"),
                InlineKeyboardButton("■ Intermediate", callback_data="study_path_intermediate")
            ],
            [
                InlineKeyboardButton("◆ Advanced", callback_data="study_path_advanced"),
                InlineKeyboardButton("● Custom", callback_data="study_path_custom")
            ],
            [
                InlineKeyboardButton("🔙 Back", callback_data="study_main_menu")
            ]
        ]),
        parse_mode='Markdown'
    )

async def handle_exit_study(query, context):
    """Exit study room"""
    # Clear study mode
    context.user_data.pop('study_mode', None)
    context.user_data.pop('study_session_id', None)
    context.user_data.pop('awaiting_study_question', None)
    
    await query.edit_message_text(
        """🚪 **LEAVING HYLOZOIC UNIVERSITY**

Thank you for studying authentic Hylozoics teachings.

You've returned to normal conversation mode. The Sacred Library is still available through:
• /sacred <search term>
• /browse_sacred

Continue your journey of understanding! 🏛️""",
        parse_mode='Markdown'
    )

async def handle_topic_study(query, context, topic):
    """Handle specific topic study"""
    # This would search for quotes related to the specific topic
    # and present them in a structured way
    
    topic_searches = {
        'consciousness': 'consciousness awareness mind',
        'development': 'development evolution growth',
        'mind': 'mind thinking thought mental',
        'love': 'love emotion feeling heart',
        'purpose': 'purpose will goal aim',
        'energy': 'energy power force',
        'reincarnation': 'reincarnation rebirth incarnation',
        'cosmic': 'cosmic universe order law'
    }
    
    search_term = topic_searches.get(topic, topic)
    
    try:
        # Search Sacred Library for topic
        quotes = await study_ai.search_sacred_library(search_term, limit=3)
        
        if quotes:
            topic_message = f"📖 **STUDYING: {topic.upper()}**\n\nHere are authentic Hylozoic teachings on this topic:\n\n"
            
            for i, quote in enumerate(quotes, 1):
                content = quote['content']
                if len(content) > 200:
                    content = content[:200] + "..."
                
                chapter = quote['metadata'].get('chapter', 'Unknown')
                language = quote['metadata'].get('language', 'unknown')
                
                topic_message += f"**{i}. {chapter} ({language.upper()})**\n"
                topic_message += f'"{content}"\n\n'
            
            keyboard = [
                [
                    InlineKeyboardButton("🔍 More Quotes", callback_data=f"study_topic_{topic}"),
                    InlineKeyboardButton("💬 Ask Question", callback_data="study_ask_question")
                ],
                [
                    InlineKeyboardButton("📚 Other Topics", callback_data="study_browse_topics"),
                    InlineKeyboardButton("🔙 Study Menu", callback_data="study_main_menu")
                ]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                topic_message,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        else:
            await query.edit_message_text(f"No quotes found for {topic}. Please try another topic.")
            
    except Exception as e:
        logger.error(f"Error in topic study: {e}")
        await query.edit_message_text("Error retrieving topic content. Please try again.")

async def process_study_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Process question asked in study mode"""
    user = update.effective_user
    message = update.message.text
    
    try:
        # Clear the awaiting flag
        context.user_data.pop('awaiting_study_question', None)
        
        # Generate Hylozoic-focused response
        person_id = uuid.uuid4()  # Temporary for now
        
        # Force Sacred Library search for study mode
        sacred_quotes = await study_ai.search_sacred_library(message, limit=3)
        vector_quotes = await study_ai.vector_search_sacred_library(message, limit=2)
        
        # Combine quotes
        all_quotes = sacred_quotes.copy()
        for vq in vector_quotes:
            if not any(q.get('material_id') == vq.get('material_id') for q in all_quotes):
                all_quotes.append(vq)
        
        if all_quotes:
            response = f"🏛️ **HYLOZOIC ANSWER TO YOUR QUESTION**\n\n"
            response += f"**Your Question:** {message}\n\n"
            response += "**From the Sacred Library:**\n\n"
            
            for i, quote in enumerate(all_quotes[:3], 1):
                content = quote['content']
                chapter = quote['metadata'].get('chapter', 'Unknown')
                language = quote['metadata'].get('language', 'unknown')
                
                response += f"**{i}. {chapter} ({language.upper()})**\n"
                response += f'"{content}"\n\n'
            
            response += "Would you like to explore any of these teachings deeper, or ask another question?"
            
            keyboard = [
                [
                    InlineKeyboardButton("🤔 Ask Another", callback_data="study_ask_question"),
                    InlineKeyboardButton("📚 Browse Topics", callback_data="study_browse_topics")
                ],
                [
                    InlineKeyboardButton("🎓 Guided Study", callback_data="study_guided"),
                    InlineKeyboardButton("🚪 Exit Study", callback_data="study_exit")
                ]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                response,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(
                "I couldn't find specific Hylozoic teachings on that topic. Would you like to try rephrasing your question or browse available topics?",
                reply_markup=InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton("📚 Browse Topics", callback_data="study_browse_topics"),
                        InlineKeyboardButton("🤔 Try Again", callback_data="study_ask_question")
                    ]
                ])
            )
        
    except Exception as e:
        logger.error(f"Error processing study question: {e}")
        await update.message.reply_text("Error processing your question. Please try again.")
