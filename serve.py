"""Start the ETH 15m tools on your computer and print the address for your iPad.

Run:  python serve.py
Stop: press Ctrl+C
"""
import http.server, socket, socketserver, webbrowser, os, sys

PORT = 8000
os.chdir(os.path.dirname(os.path.abspath(__file__)))

def lan_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80)); return s.getsockname()[0]
    except OSError:
        return "127.0.0.1"
    finally:
        s.close()

class Handler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-store"); super().end_headers()
    def log_message(self, *a): pass

socketserver.TCPServer.allow_reuse_address = True
with socketserver.TCPServer(("0.0.0.0", PORT), Handler) as httpd:
    ip = lan_ip()
    print("ETH 15m tools are running.")
    print("  This computer:  http://localhost:%d/" % PORT)
    print("  iPad or phone:  http://%s:%d/   (same Wi-Fi)" % (ip, PORT))
    print("Leave this window open. Press Ctrl+C to stop.")
    if "--no-browser" not in sys.argv:
        webbrowser.open("http://localhost:%d/" % PORT)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
