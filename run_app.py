"""
PolicyBuzar - Quick Start Application Runner
Starts the complete full-stack PolicyBuzar platform on http://127.0.0.1:5000
"""

import sys
import os

# Fix Windows console encoding for UTF-8
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Ensure project root is in python path
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from backend.app import app

if __name__ == "__main__":
    print("=" * 70)
    print("  [SALESINTERNAI] DYNAMIC AI CUSTOMER CLASSIFICATION & ROUTING")
    print("=" * 70)
    print("  Full-Stack Application is running on: http://127.0.0.1:5000")
    print("  API Endpoints active at:              http://127.0.0.1:5000/api")
    print("  To run frontend in Vite dev mode:    cd frontend && npm run dev")
    print("=" * 70)
    app.run(host="0.0.0.0", port=5000, debug=False)
