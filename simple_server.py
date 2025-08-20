#!/usr/bin/env python3
import os
import http.server
import socketserver
import json

class SimpleHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {'status': 'healthy', 'service': 'simple-server'}
            self.wfile.write(json.dumps(response).encode())
        elif self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {'message': 'Simple server working!', 'status': 'success'}
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not found')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    print(f"Starting simple server on port {port}")
    
    with socketserver.TCPServer(("", port), SimpleHandler) as httpd:
        print(f"Server running on port {port}")
        httpd.serve_forever()
