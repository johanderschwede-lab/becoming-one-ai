# 🚀 Railway Deployment Guide for Becoming One™ AI Bot

## Step 1: Install Railway CLI
```bash
# Install Railway CLI
npm install -g @railway/cli

# Or using curl
curl -fsSL https://railway.app/install.sh | sh
```

## Step 2: Login to Railway
```bash
railway login
```
This will open your browser to authenticate.

## Step 3: Initialize Project
```bash
# In your project directory
railway init

# Select your existing project: web-production-e95b8
```

## Step 4: Set Environment Variables
```bash
# Set all your environment variables
railway variables set SUPABASE_URL="https://emgidzzjpjtujozttzyv.supabase.co"
railway variables set SUPABASE_ANON_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVtZ2lkenpqcGp0dWpvenR0enl2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTUxNTMyMDksImV4cCI6MjA3MDcyOTIwOX0.JpMhtzZFqSP1C9BFcWypfZ2o9m8jheKoQgfhwFxUWxQ"
railway variables set PINECONE_API_KEY="pcsk_2nX8US_Mku3PJmJ7hoe67kaw1tGHL7TwerFJ5zsjuakrSMjkvm1JcCDurxFpXcGDWd7yju"
railway variables set OPENAI_API_KEY="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"
railway variables set TELEGRAM_BOT_TOKEN="8244158767:AAGJveKJcOwFO_PxaeROpiQ7FKGSv-0aFrQ"
railway variables set PINECONE_ENVIRONMENT="us-east-1"
railway variables set PINECONE_INDEX_NAME="becoming-one-embeddings"
railway variables set DEBUG="false"
railway variables set LOG_LEVEL="info"
railway variables set ENVIRONMENT="production"
```

## Step 5: Deploy
```bash
railway up
```

## Step 6: Check Status
```bash
railway status
railway logs
```

## Step 7: Get Your Domain
```bash
railway domain
```

Your bot will be running 24/7 at the provided URL!

## Troubleshooting
- Check logs: `railway logs`
- Restart service: `railway restart`
- Check variables: `railway variables`

## 🎉 Success!
Once deployed, your bot runs independently of your computer!
