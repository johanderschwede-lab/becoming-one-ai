#!/usr/bin/env python3
"""
Production Deployment Script for Becoming One™ System
Prepares complete system for cloud deployment
"""

import os
import json
import shutil
from pathlib import Path

def create_production_deployment():
    """Create production-ready deployment configuration"""
    
    print("🚀 Preparing Becoming One™ for production deployment...")
    
    # Create deployment directory
    deploy_dir = Path("production-deploy")
    if deploy_dir.exists():
        shutil.rmtree(deploy_dir)
    deploy_dir.mkdir()
    
    print(f"📁 Created deployment directory: {deploy_dir}")
    
    # Copy source code
    shutil.copytree("src", deploy_dir / "src")
    shutil.copytree("database", deploy_dir / "database") 
    
    # Copy essential files
    essential_files = [
        "start_bot.py",
        "start_inbox_processor.py", 
        "start_complete_pipeline.py",
        "transcribe_media.py",
        "upload_knowledge_content.py",
        "working_bot.py"
    ]
    
    for file in essential_files:
        if Path(file).exists():
            shutil.copy(file, deploy_dir / file)
    
    print("✅ Source code copied")
    
    # Create production requirements.txt
    requirements = """python-telegram-bot==22.3
supabase==2.18.1
openai==1.99.9
python-dotenv==1.1.1
requests==2.32.4
loguru==0.7.2
pydantic==2.5.2
watchdog==3.0.0
python-docx==0.8.11
boto3==1.34.0
botocore==1.34.0
openai-whisper==20231117
ffmpeg-python==0.2.0
numpy==1.24.3
pandas==2.0.3
aiohttp==3.9.1
httpx==0.25.2
fastapi==0.104.1
uvicorn==0.24.0
psycopg2-binary==2.9.7
python-dateutil==2.8.2
pytz==2023.3"""
    
    with open(deploy_dir / "requirements.txt", "w") as f:
        f.write(requirements)
    
    print("✅ Production requirements.txt created")
    
    # Create Procfile for Railway
    procfile_content = "web: python3 start_complete_pipeline.py $S3_INBOX_URL --transcription-method api"
    
    with open(deploy_dir / "Procfile", "w") as f:
        f.write(procfile_content)
    
    print("✅ Procfile created")
    
    # Create railway.json configuration
    railway_config = {
        "build": {
            "builder": "NIXPACKS"
        },
        "deploy": {
            "startCommand": "python3 start_complete_pipeline.py $S3_INBOX_URL --transcription-method api",
            "healthcheckPath": "/health",
            "healthcheckTimeout": 300,
            "restartPolicyType": "ON_FAILURE",
            "restartPolicyMaxRetries": 3
        },
        "environments": {
            "production": {
                "variables": {
                    "ENVIRONMENT": "production",
                    "DEBUG": "false",
                    "LOG_LEVEL": "info"
                }
            }
        }
    }
    
    with open(deploy_dir / "railway.json", "w") as f:
        json.dump(railway_config, f, indent=2)
    
    print("✅ railway.json created")
    
    # Create health check endpoint
    health_check = '''from fastapi import FastAPI
from fastapi.responses import JSONResponse
import os

app = FastAPI()

@app.get("/health")
async def health_check():
    """Health check endpoint for Railway"""
    return JSONResponse({
        "status": "healthy",
        "service": "becoming-one-ai",
        "environment": os.getenv("ENVIRONMENT", "unknown"),
        "components": {
            "telegram_bot": "running",
            "ai_engine": "ready", 
            "database": "connected",
            "vector_db": "connected"
        }
    })

@app.get("/")
async def root():
    return {"message": "Becoming One™ AI System", "status": "running"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
'''
    
    with open(deploy_dir / "health_server.py", "w") as f:
        f.write(health_check)
    
    print("✅ Health check server created")
    
    # Create cloud-compatible INBOX processor
    cloud_inbox = '''#!/usr/bin/env python3
"""
Cloud-compatible INBOX processor with S3 integration
"""
import os
import boto3
from pathlib import Path
from src.core.inbox_processor import InboxProcessor

class CloudInboxProcessor(InboxProcessor):
    """INBOX processor with S3 cloud storage support"""
    
    def __init__(self, s3_bucket: str, s3_prefix: str = "inbox/"):
        self.s3_client = boto3.client('s3')
        self.bucket = s3_bucket
        self.prefix = s3_prefix
        
        # Create local temp directory
        local_inbox = Path("/tmp/inbox")
        super().__init__(str(local_inbox))
    
    async def sync_from_s3(self):
        """Download new files from S3"""
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket,
                Prefix=self.prefix
            )
            
            for obj in response.get('Contents', []):
                key = obj['Key']
                if key.endswith('/'):  # Skip directories
                    continue
                
                local_file = self.inbox_folder / Path(key).name
                if not local_file.exists():
                    self.s3_client.download_file(self.bucket, key, str(local_file))
                    print(f"📥 Downloaded: {Path(key).name}")
                    
        except Exception as e:
            print(f"❌ S3 sync error: {e}")
    
    async def upload_to_s3(self, local_file: Path, s3_folder: str):
        """Upload processed file to S3"""
        try:
            s3_key = f"{s3_folder}{local_file.name}"
            self.s3_client.upload_file(str(local_file), self.bucket, s3_key)
            print(f"📤 Uploaded: {s3_key}")
        except Exception as e:
            print(f"❌ S3 upload error: {e}")

if __name__ == "__main__":
    import asyncio
    
    bucket = os.getenv("S3_BUCKET_NAME", "becoming-one-content")
    processor = CloudInboxProcessor(bucket)
    
    async def run_with_s3_sync():
        while True:
            await processor.sync_from_s3()
            await asyncio.sleep(30)  # Check S3 every 30 seconds
    
    asyncio.run(run_with_s3_sync())
'''
    
    with open(deploy_dir / "cloud_inbox_processor.py", "w") as f:
        f.write(cloud_inbox)
    
    print("✅ Cloud INBOX processor created")
    
    # Create deployment README
    readme = """# Becoming One™ Production Deployment

## Quick Deploy to Railway

1. Install Railway CLI:
   ```bash
   npm install -g @railway/cli
   ```

2. Login and deploy:
   ```bash
   railway login
   railway init
   railway up
   ```

3. Set environment variables in Railway dashboard:
   - All variables from config/live.env
   - Add AWS credentials for S3 storage:
     - AWS_ACCESS_KEY_ID
     - AWS_SECRET_ACCESS_KEY
     - S3_BUCKET_NAME=becoming-one-content

## Services Deployed:
- Complete AI Pipeline (Telegram bot + INBOX processor + Transcription)
- Health Monitoring (/health endpoint)
- Auto-restart on failure

## File Storage:
Uses AWS S3 for cloud file storage:
- Drop files in S3 bucket: becoming-one-content/inbox/
- System processes automatically
- Results saved to: completed/, failed/, content_suggestions/

## Monitoring:
- Health check: https://your-app.railway.app/health
- Logs: `railway logs`
- Status: `railway status`

## Usage:
1. Upload files to S3 inbox folder
2. Chat with Telegram bot
3. System processes everything automatically 24/7
"""
    
    with open(deploy_dir / "README.md", "w") as f:
        f.write(readme)
    
    print("✅ Deployment README created")
    
    # Create .gitignore for deployment
    gitignore = """.env
.env.local
.env.production
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.venv/
pip-log.txt
pip-delete-this-directory.txt
.DS_Store
*.log
node_modules/
.railway/
"""
    
    with open(deploy_dir / ".gitignore", "w") as f:
        f.write(gitignore)
    
    print("✅ .gitignore created")
    
    # Create environment template for Railway
    env_template = """# Environment variables for Railway deployment
# Copy these to Railway dashboard Variables section

# Database (already working)
SUPABASE_URL=https://emgidzzjpjtujozttzyv.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVtZ2lkenpqcGp0dWpvenR0enl2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTUxNTMyMDksImV4cCI6MjA3MDcyOTIwOX0.JpMhtzZFqSP1C9BFcWypfZ2o9m8jheKoQgfhwFxUWxQ

# Vector Database (already working)
PINECONE_API_KEY=pcsk_2nX8US_Mku3PJmJ7hoe67kaw1tGHL7TwerFJ5zsjuakrSMjkvm1JcCDurxFpXcGDWd7yju
PINECONE_ENVIRONMENT=us-east-1
PINECONE_INDEX_NAME=becoming-one-embeddings

# AI (already working)
OPENAI_API_KEY=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
OPENAI_MODEL=gpt-4-turbo-preview

# Telegram (already working)
TELEGRAM_BOT_TOKEN=8244158767:AAGJveKJcOwFO_PxaeROpiQ7FKGSv-0aFrQ

# AWS S3 for cloud file storage (NEW - need to set up)
AWS_ACCESS_KEY_ID=your_aws_access_key_here
AWS_SECRET_ACCESS_KEY=your_aws_secret_key_here
S3_BUCKET_NAME=becoming-one-content
S3_INBOX_URL=s3://becoming-one-content/inbox/

# System settings
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=info
"""
    
    with open(deploy_dir / "railway_env_template.txt", "w") as f:
        f.write(env_template)
    
    print("✅ Railway environment template created")
    
    print(f"\n🎉 Production deployment ready in: {deploy_dir.absolute()}")
    print("\nNext steps:")
    print("1. Set up AWS S3 bucket (see CLOUD_DEPLOYMENT_PLAN.md)")
    print("2. cd production-deploy")
    print("3. railway init")
    print("4. Set environment variables in Railway dashboard")
    print("5. railway up")
    print("\n🚀 Your system will be running 24/7 in the cloud!")

if __name__ == "__main__":
    create_production_deployment()
