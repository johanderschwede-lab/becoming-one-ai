#!/usr/bin/env python3
import os
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return {'message': 'Minimal test working!', 'status': 'success'}

@app.route('/health')
def health():
    return {'status': 'healthy', 'service': 'minimal-test'}

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    print(f"Starting minimal test on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
