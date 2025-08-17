# Getting Started with Becoming One™ AI Journey System

## Quick Setup Guide

### 1. Prerequisites
- Python 3.8+ installed
- Supabase account and project
- Pinecone account and API key
- OpenAI API key
- Telegram Bot Token (from @BotFather)
- Make.com account (optional but recommended)

### 2. Environment Setup

1. **Clone/Navigate to project directory:**
   ```bash
   cd ~/Documents/becoming-one-ai
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables:**
   ```bash
   cp config/env.example .env
   # Edit .env with your actual API keys and credentials
   ```

4. **Set up Supabase database:**
   ```bash
   python scripts/setup_database.py
   ```

### 3. API Keys and Services Setup

#### Supabase Setup
1. Create a new project at [supabase.com](https://supabase.com)
2. Go to Settings > API
3. Copy your URL and anon key to `.env`
4. Copy your service_role key (needed for database setup)

#### Pinecone Setup
1. Create account at [pinecone.io](https://pinecone.io)
2. Create a new index named `becoming-one-embeddings`
3. Use dimension: 1536, metric: cosine
4. Copy API key to `.env`

#### OpenAI Setup
1. Get API key from [platform.openai.com](https://platform.openai.com)
2. Add to `.env` file

#### Telegram Bot Setup
1. Message @BotFather on Telegram
2. Create new bot with `/newbot`
3. Copy bot token to `.env`

#### Make.com Setup (Optional)
1. Create account at [make.com](https://make.com)
2. Set up webhook scenarios for automation
3. Add webhook URL to `.env`

### 4. Running the System

#### Start Telegram Bot
```bash
python src/bots/telegram/telegram_bot.py
```

#### Test Database Connection
```bash
python scripts/setup_database.py --verify-only
```

### 5. First Steps

1. **Test your Telegram bot:**
   - Find your bot on Telegram
   - Send `/start` command
   - Have a conversation!

2. **Monitor logs:**
   - Check console output for any errors
   - Verify database entries in Supabase dashboard

3. **Explore the system:**
   - Try different conversation topics
   - Check `/profile` command
   - Test consent management with `/consent`

## Project Structure Overview

```
becoming-one-ai/
├── src/
│   ├── bots/telegram/          # Telegram bot implementation
│   ├── core/                   # Core AI and Becoming One™ method
│   ├── database/              # Supabase models and operations
│   ├── integrations/          # Third-party service integrations
│   └── utils/                 # Shared utilities
├── database/schemas/          # Database schema files
├── scripts/                   # Setup and utility scripts
└── docs/                     # Documentation
```

## Key Features

### ✅ Phase 1 (Current)
- **Telegram Bot**: Full conversation handling
- **Identity Management**: Cross-platform user tracking
- **Vector Search**: Context-aware responses using Pinecone
- **Database Logging**: All interactions stored in Supabase
- **Becoming One™ Method**: Personalized mentorship approach

### 🔄 Coming Next
- YouTube integration
- Email bot
- TikTok integration
- BuddyBoss platform
- Advanced analytics dashboard

## Troubleshooting

### Common Issues

1. **Database Connection Errors**
   - Verify Supabase URL and keys in `.env`
   - Check if database tables were created properly
   - Run `python scripts/setup_database.py --verify-only`

2. **Pinecone Errors**
   - Verify API key and environment in `.env`
   - Check if index exists and has correct dimensions

3. **OpenAI API Errors**
   - Verify API key is valid and has credits
   - Check rate limits

4. **Telegram Bot Not Responding**
   - Verify bot token is correct
   - Check if webhook URL conflicts exist
   - Look for error messages in console

### Getting Help

1. Check the logs for detailed error messages
2. Verify all environment variables are set correctly
3. Test each component individually
4. Review the code documentation in each module

## Development Tips

1. **Start Small**: Test with Telegram bot first
2. **Check Logs**: Use the loguru logging to debug issues
3. **Test Database**: Use Supabase dashboard to verify data
4. **Iterate**: The system learns from conversations

## Next Steps

Once you have the basic system running:

1. **Customize the Becoming One™ Method**: Edit `src/core/becoming_one_method.py`
2. **Add Knowledge Base Content**: Use Pinecone client to store method materials
3. **Set up Make.com Workflows**: Automate cross-platform integration
4. **Expand to Other Platforms**: Add YouTube, Email, etc.

Welcome to your Becoming One™ AI Journey! 🌟
