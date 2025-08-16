# Becoming One™ AI Journey System

## Vision
Create an AI-powered omnichannel mentor system that:
1. Recognizes and adapts to users across all platforms (Telegram, YouTube, TikTok, Email, BuddyBoss, etc.)
2. Delivers personalized, evolving guidance through the Becoming One™ method
3. Supports Johan & Marianne in evolving the method itself as a living, co-creative Muse

## Project Structure

```
becoming-one-ai/
├── src/
│   ├── bots/              # Platform-specific bot implementations
│   │   ├── telegram/      # Telegram bot
│   │   ├── youtube/       # YouTube integration
│   │   └── email/         # Email integration
│   ├── core/              # Core AI logic and Becoming One™ method
│   │   ├── ai_engine.py   # Main AI processing
│   │   ├── becoming_one_method.py # Core methodology
│   │   └── personalization.py # User adaptation logic
│   ├── database/          # Database models and operations
│   │   ├── models.py      # Supabase models
│   │   └── operations.py  # Database operations
│   ├── integrations/      # Third-party service integrations
│   │   ├── pinecone_client.py # Vector search
│   │   ├── openai_client.py   # GPT integration
│   │   └── make_webhooks.py   # Make.com integration
│   └── utils/             # Shared utilities
├── config/                # Configuration files
├── database/              # Database schemas and migrations
│   ├── schemas/           # Supabase table schemas
│   └── migrations/        # Database migration scripts
├── docs/                  # Documentation
├── scripts/               # Deployment and utility scripts
└── tests/                 # Test files
```

## Phase 1: Foundation (August 2025)
**Goal**: Working Telegram bot with Pinecone retrieval and Supabase identity logging

### ✅ DONE:
- Telegram bot responding to queries via Make.com scenario
- Pinecone vector search integrated (context-aware)

### 🔄 TO DO:
1. **Supabase Setup**
   - Create tables: identity_registry, event_log, channel_mapping
   - Enable webhooks for event inserts
   - Set up person_id enrichment for GPT prompts

2. **Make.com Modules**
   - Connect Supabase HTTP API
   - Set up Telegram message handling
   - Implement person_id lookup and content insertion

3. **Tagging & Metadata Layer**
   - Add basic tagging to events (identity, confusion, fear, etc.)
   - Store tags in metadata for Pinecone records
   - Use tag-based filtering in queries

## Tech Stack
- **Database**: Supabase (PostgreSQL)
- **Vector Search**: Pinecone
- **Automation**: Make.com
- **Platforms**: Telegram, YouTube, TikTok, Email, BuddyBoss
- **AI**: OpenAI GPT integration
- **Languages**: Python, JavaScript/Node.js

## Getting Started
1. Copy `.env.example` to `.env` and fill in your API keys
2. Install dependencies: `pip install -r requirements.txt`
3. Set up Supabase database using schemas in `database/schemas/`
4. Configure Make.com scenarios
5. Test Telegram bot integration

## Environment Variables Needed
- `SUPABASE_URL`
- `SUPABASE_ANON_KEY`
- `PINECONE_API_KEY`
- `OPENAI_API_KEY`
- `TELEGRAM_BOT_TOKEN`
- `MAKE_WEBHOOK_URL`
