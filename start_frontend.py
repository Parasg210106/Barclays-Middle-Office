import http.server
import socketserver
import os

PORT = 8080
WEB_DIR = os.path.join(os.path.dirname(__file__), 'Frontend', 'public')
os.chdir(WEB_DIR)

Handler = http.server.SimpleHTTPRequestHandler

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Serving frontend at http://localhost:{PORT}/ (Press CTRL+C to quit)")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server.") 