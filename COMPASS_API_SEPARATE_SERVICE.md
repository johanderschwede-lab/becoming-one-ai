# Compass API - Separate Railway Service Setup

## Problem
The existing Telegram bot and the new Compass API are conflicting because they both try to use the same bot token. This causes the "Conflict: terminated by other getUpdates request" error.

## Solution
Create a separate Railway service for the Compass API while keeping the existing bot running.

## Steps to Deploy

### 1. Create New Railway Service
```bash
# Create a new service in the same Railway project
railway service create compass-api
```

### 2. Set Service Configuration
```bash
# Switch to the compass-api service
railway service compass-api

# Set the start command for this service
railway variables set START_COMMAND="python compass_api.py"
```

### 3. Configure Environment Variables
Add these environment variables to the compass-api service:
- `COMPASS_BOT_TOKEN` - Your new Compass Management Bot token
- `TELEGRAM_CHAT_ID` - Your chat ID (1139989892)
- `SUPABASE_URL` - Your Supabase URL
- `SUPABASE_ANON_KEY` - Your Supabase anon key
- `OPENAI_API_KEY` - Your OpenAI API key

### 4. Deploy the Service
```bash
# Deploy the compass-api service
railway up --service compass-api
```

### 5. Get the New API URL
```bash
# Get the URL for the compass-api service
railway domain --service compass-api
```

### 6. Update HTML File
Update the `compass_management.html` file with the new API URL:
```javascript
let apiBaseUrl = 'https://your-compass-api-service.up.railway.app/api';
```

## Alternative: Manual Railway Dashboard Setup

1. Go to Railway Dashboard
2. Select your project
3. Click "New Service" → "GitHub Repo"
4. Select the same repository
5. Name it "compass-api"
6. Set the root directory to `/` (or create a subdirectory)
7. Set the start command to `python compass_api.py`
8. Add environment variables
9. Deploy

## Verification

After deployment, test the new service:
```bash
# Test the health endpoint
curl https://your-compass-api-service.up.railway.app/health

# Test the API
curl https://your-compass-api-service.up.railway.app/api/stats
```

## Benefits of Separate Services

1. **No Conflicts**: Each service runs independently
2. **Independent Scaling**: Can scale services separately
3. **Better Monitoring**: Separate logs and metrics
4. **Easier Debugging**: Isolated issues
5. **Different Resources**: Can allocate different resources per service

## Current Status
- ✅ Main bot service: `working_bot.py` (existing)
- 🔄 Compass API service: `compass_api.py` (new separate service)
- ✅ HTML interface: `compass_management.html` (ready to update with new URL)
