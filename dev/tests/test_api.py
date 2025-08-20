#!/usr/bin/env python3
"""
Minimal test API for Railway debugging
"""

import os
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        'message': 'Test API is working!',
        'status': 'success',
        'port': os.environ.get('PORT', 'unknown')
    })

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'service': 'test-api'
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    print(f"Starting test API on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
