#!/usr/bin/env python
"""Alternative startup script for SQLite backend"""

import sys
import os

# Ensure proper path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app

if __name__ == '__main__':
    print("Starting Inventory Management System (SQLite)...")
    app = create_app(use_sqlite=True)
    print("Server starting on http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
