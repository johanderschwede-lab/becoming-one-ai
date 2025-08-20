# Railway Environment Variables Setup

## How to Update Environment Variables

### 1. Access Railway Dashboard
- Go to: https://railway.app/dashboard
- Login with your account
- Find project: **brave-gratitude**
- Click on service: **becoming-one-ai**

### 2. Update Variables
- Click on **Variables** tab
- Find the variable you want to update
- Click **Edit** button
- Paste new value
- Click **Save**
- Railway will automatically redeploy

### 3. Required Variables

#### Core API Keys
```
OPENAI_API_KEY=sk-proj-your-new-key-here
TELEGRAM_BOT_TOKEN=your-bot-token
```

#### Database
```
SUPABASE_URL=https://emgidzzjpjtujozttzyv.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
```

#### Vector Database
```
PINECONE_API_KEY=your-pinecone-key
PINECONE_ENVIRONMENT=us-east-1
PINECONE_INDEX_NAME=becoming-one-embeddings
```

## Getting New API Keys

### OpenAI API Key
1. Go to: https://platform.openai.com/api-keys
2. Click **Create new secret key**
3. Copy the key (starts with `sk-proj-`)
4. Update in Railway Variables
5. Test locally first: `python3 scripts/test_bot_offline.py`

### Telegram Bot Token
1. Message @BotFather on Telegram
2. Use `/mybots` to see your bots
3. Select your bot → API Token
4. Copy the token
5. Update in Railway Variables

### Supabase Keys
1. Go to: https://supabase.com/dashboard
2. Select your project
3. Go to Settings → API
4. Copy the keys you need
5. Update in Railway Variables

## Testing After Updates

### Local Testing
```bash
# Update local .env file with same values
python3 scripts/create_local_env.py

# Test locally
python3 scripts/test_bot_offline.py
python3 scripts/dev_env.py --verify
```

### Railway Deployment
- Railway automatically redeploys when you save variables
- Check deployment logs in Railway dashboard
- Test bot functionality after deployment

## Troubleshooting

### Invalid API Key Errors
- Double-check the key format
- Ensure no extra spaces or characters
- Test the key in a simple API call first
- Check if the key has required permissions

### Deployment Failures After Variable Update
- Check Railway logs for specific errors
- Verify all required variables are set
- Test locally with same environment variables
- Roll back to previous values if needed

## Security Best Practices

### API Key Management
- Never commit API keys to git
- Use different keys for development/production
- Rotate keys regularly
- Monitor usage for unusual activity

### Environment Sync
- Keep local `.env` in sync with Railway
- Document all required variables
- Test changes locally before deploying
- Have backup keys ready
