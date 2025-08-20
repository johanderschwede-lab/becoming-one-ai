#!/usr/bin/env python3
"""
Compass Management API - Railway Optimized Version
"""

import os
import sys
import json
import requests
from datetime import datetime

# Try to import Flask, install if missing
try:
    from flask import Flask, jsonify, request, send_from_directory
    from flask_cors import CORS
except ImportError:
    print("Flask not found, installing...")
    os.system(f"{sys.executable} -m pip install flask flask-cors")
    from flask import Flask, jsonify, request, send_from_directory
    from flask_cors import CORS

# Try to import dotenv
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("python-dotenv not found, installing...")
    os.system(f"{sys.executable} -m pip install python-dotenv")
    from dotenv import load_dotenv
    load_dotenv()

app = Flask(__name__)
CORS(app)

# Configuration
EXPORT_DIR = "EXPORT"
DOCS_TO_PROCESS_DIR = "documents_to_process"
LOGS_DIR = "logs"

# Bot configuration
COMPASS_BOT_TOKEN = os.environ.get('COMPASS_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID', '1139989892')

def send_compass_notification(message):
    """Send notification using the Compass Management Bot"""
    if not COMPASS_BOT_TOKEN:
        print("Warning: COMPASS_BOT_TOKEN not set")
        return False
    
    try:
        url = f"https://api.telegram.org/bot{COMPASS_BOT_TOKEN}/sendMessage"
        data = {
            'chat_id': TELEGRAM_CHAT_ID,
            'text': f"🔧 Compass System: {message}",
            'parse_mode': 'HTML'
        }
        response = requests.post(url, data=data, timeout=10)
        return response.status_code == 200
    except Exception as e:
        print(f"Error sending notification: {e}")
        return False

@app.route('/')
def serve_html():
    """Serve the HTML management interface"""
    try:
        return send_from_directory('.', 'compass_management.html')
    except:
        return jsonify({
            'message': 'Compass Management API is running!',
            'endpoints': [
                '/api/stats',
                '/api/review-queue',
                '/health'
            ]
        })

@app.route('/api/stats')
def get_stats():
    """Get system statistics"""
    try:
        stats = {
            'total_files': 0,
            'compass_core': 0,
            'human_review': 0,
            'quarantine': 0,
            'last_updated': datetime.now().isoformat(),
            'status': 'success'
        }
        
        # Count files in each directory if they exist
        if os.path.exists(EXPORT_DIR):
            for root, dirs, files in os.walk(EXPORT_DIR):
                if 'COMPASS_CORE' in root:
                    stats['compass_core'] += len(files)
                elif 'HUMAN_REVIEW' in root:
                    stats['human_review'] += len(files)
                elif 'QUARANTINE_RESCUE' in root:
                    stats['quarantine'] += len(files)
                stats['total_files'] += len(files)
        
        return jsonify(stats)
    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error',
            'total_files': 0,
            'compass_core': 0,
            'human_review': 0,
            'quarantine': 0,
            'last_updated': datetime.now().isoformat()
        }), 500

@app.route('/api/review-queue')
def get_review_queue():
    """Get items in the human review queue"""
    try:
        review_items = []
        review_dir = os.path.join(EXPORT_DIR, "HUMAN_REVIEW")
        
        if os.path.exists(review_dir):
            for root, dirs, files in os.walk(review_dir):
                for file in files:
                    if file.endswith('.md') and not file.endswith('.meta.json'):
                        file_path = os.path.join(root, file)
                        meta_path = file_path + '.meta.json'
                        
                        # Get file stats
                        stat = os.stat(file_path)
                        
                        item = {
                            'filename': file,
                            'path': os.path.relpath(file_path, EXPORT_DIR),
                            'size': stat.st_size,
                            'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                            'category': os.path.basename(root),
                            'score': 'N/A',
                            'decision': 'N/A'
                        }
                        
                        # Try to get metadata
                        if os.path.exists(meta_path):
                            try:
                                with open(meta_path, 'r') as f:
                                    metadata = json.load(f)
                                    strategic_score = metadata.get('strategic_score', {})
                                    item['score'] = strategic_score.get('total_score', 'N/A')
                                    item['decision'] = strategic_score.get('processing_decision', 'N/A')
                            except:
                                pass
                        
                        review_items.append(item)
        
        return jsonify(review_items)
    except Exception as e:
        return jsonify({'error': str(e), 'items': []}), 500

@app.route('/api/approve/<filename>')
def approve_item(filename):
    """Approve an item and move it to compass core"""
    try:
        # Send notification about approval
        send_compass_notification(f"✅ Approved: {filename}")
        
        return jsonify({'status': 'success', 'message': f'Approved {filename}'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/move-to-consider/<filename>')
def move_to_consider(filename):
    """Move an item to the consider list"""
    try:
        # Send notification about move to consider
        send_compass_notification(f"📋 Moved to Consider: {filename}")
        
        return jsonify({'status': 'success', 'message': f'Moved {filename} to consider list'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/test-notification')
def test_notification():
    """Test notification system"""
    try:
        success = send_compass_notification("🧪 Test notification from Compass Management API")
        return jsonify({
            'status': 'success' if success else 'error',
            'message': 'Test notification sent' if success else 'Failed to send notification'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/start-watcher')
def start_watcher():
    """Start the folder watcher"""
    try:
        # Send notification about watcher start
        send_compass_notification("🚀 Folder watcher started")
        
        return jsonify({'status': 'success', 'message': 'Folder watcher started'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/logs')
def get_logs():
    """Get recent logs"""
    try:
        logs = []
        if os.path.exists(LOGS_DIR):
            for file in os.listdir(LOGS_DIR):
                if file.endswith('.log'):
                    file_path = os.path.join(LOGS_DIR, file)
                    with open(file_path, 'r') as f:
                        content = f.read()
                        logs.append({
                            'filename': file,
                            'content': content[-1000:]  # Last 1000 characters
                        })
        return jsonify(logs)
    except Exception as e:
        return jsonify({'error': str(e), 'logs': []}), 500

@app.route('/health')
def health_check():
    """Health check endpoint for Railway"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'compass-api',
        'environment': os.environ.get('RAILWAY_ENVIRONMENT', 'unknown'),
        'port': os.environ.get('PORT', 'unknown'),
        'compass_bot_configured': bool(COMPASS_BOT_TOKEN)
    })

@app.route('/debug')
def debug_info():
    """Debug information for troubleshooting"""
    return jsonify({
        'python_version': sys.version,
        'working_directory': os.getcwd(),
        'files_in_directory': os.listdir('.'),
        'environment_variables': {
            'PORT': os.environ.get('PORT'),
            'RAILWAY_ENVIRONMENT': os.environ.get('RAILWAY_ENVIRONMENT'),
            'RAILWAY_SERVICE_NAME': os.environ.get('RAILWAY_SERVICE_NAME'),
            'COMPASS_BOT_TOKEN': '***' if COMPASS_BOT_TOKEN else 'NOT_SET',
            'TELEGRAM_CHAT_ID': TELEGRAM_CHAT_ID
        }
    })

if __name__ == '__main__':
    # Use Railway's PORT environment variable or default to 5001
    port = int(os.environ.get('PORT', 5001))
    
    print(f"🌐 Starting Compass Management API...")
    print(f"📱 Port: {port}")
    print(f"🔧 Environment: {os.environ.get('RAILWAY_ENVIRONMENT', 'local')}")
    print(f"📁 Working directory: {os.getcwd()}")
    print(f"📋 Files in directory: {os.listdir('.')}")
    print(f"🤖 Compass Bot configured: {bool(COMPASS_BOT_TOKEN)}")
    
    # Send startup notification
    if COMPASS_BOT_TOKEN:
        send_compass_notification("🚀 Compass Management API started")
    
    # Run the app
    app.run(host='0.0.0.0', port=port, debug=False)
