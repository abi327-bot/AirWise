"""
app.py
Web server for the AirWise project (Stage 6 Unified Integration).
Communicates directly with the master airwise_core coordinator to serve
the live and predictive environmental dashboard.
"""

import os
import webbrowser

# Safe Flask import with zero-dependency fallback
try:
    from flask import Flask, render_template, request
    HAS_FLASK = True
except ImportError:
    HAS_FLASK = False

# Import the master unified state coordinator from airwise_core
from airwise_core import get_airwise_state

# ==========================================
# 1. FLASK IMPLEMENTATION
# ==========================================
if HAS_FLASK:
    app = Flask(__name__)

    @app.route("/", methods=["GET", "POST"])
    def home():
        # Get requested city from search form or URL parameter
        requested_city = request.form.get("city") or request.args.get("city")

        # Retrieve the master unified state (synchronizes data, graphs, and advice)
        state = get_airwise_state(requested_city)

        # Unpack state dictionary cleanly into Jinja2 template
        return render_template("index.html", **state)

# ==========================================
# 2. ZERO-DEPENDENCY BUILT-IN FALLBACK
# ==========================================
else:
    from http.server import HTTPServer, SimpleHTTPRequestHandler

    class AirWiseFallbackHandler(SimpleHTTPRequestHandler):
        def do_GET(self):
            if self.path in ("/", "/index.html"):
                self.path = "/index.html"
            return super().do_GET()

# ==========================================
# 3. SERVER RUNNER
# ==========================================
if __name__ == "__main__":
    PORT = 5000
    URL = f"http://127.0.0.1:{PORT}"

    print("=" * 60)
    print("🌿 AirWise Integrated Web Server starting...")
    if HAS_FLASK:
        print("Running in Flask mode connected to shared airwise_core.")
    else:
        print("Running in zero-dependency built-in mode.")
        print("Tip: Run 'pip install flask requests matplotlib' for full live mode.")
    print(f"👉 Opening your browser at: {URL}")
    print("Press Ctrl + C in this terminal to stop.")
    print("=" * 60)

    webbrowser.open(URL)

    if HAS_FLASK:
        app.run(debug=True, port=PORT)
    else:
        server_address = ("127.0.0.1", PORT)
        httpd = HTTPServer(server_address, AirWiseFallbackHandler)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped. Goodbye!")
            httpd.server_close()
