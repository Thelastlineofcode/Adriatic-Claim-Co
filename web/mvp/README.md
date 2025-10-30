# Adriatic Claim Co — MVP local run instructions

This folder contains a tiny static intake form and a Flask stub to test intake submissions locally.

Quick steps (macOS / zsh):

1. Create a Python virtualenv and install Flask (if you don't have one):

```bash
cd /Users/houseofobi/Documents/GitHub/Adriatic-Claim-Co
python3 -m venv backend/.venv
source backend/.venv/bin/activate
pip install flask
```

2. Run the Flask stub:

```bash
python3 backend/mvp_server.py
# Server runs at http://127.0.0.1:5001
```

3. Serve the static files (one simple option):

```bash
# from the repo web/mvp directory
python3 -m http.server 8000 --directory web/mvp
# Open http://127.0.0.1:8000/intake.html in your browser
```

Notes & CORS

- The intake form posts to `http://127.0.0.1:5001/api/claims`. If you serve static files from a different origin/port, the browser may block cross-origin requests. For local testing, either serve static files from the same origin or enable/allow CORS on your Flask stub (e.g., install `flask-cors` and add `CORS(app)`).

Security

- The Flask stub and admin page are development-only and lack authentication. Do not expose them publicly.
