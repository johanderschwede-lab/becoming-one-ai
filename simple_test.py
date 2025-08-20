#!/usr/bin/env python3
"""
Simple test API for Railway deployment verification
"""

import os
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        'message': 'Simple test API is working!',
        'service': 'compass-api-test',
        'timestamp': '2025-08-20'
    })

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'service': 'compass-api-test'
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    print(f"Starting simple test API on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
