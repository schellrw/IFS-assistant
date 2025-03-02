#!/usr/bin/env python
"""
Development server script for running the application locally.
"""
import os
from backend.app import create_app
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

if __name__ == "__main__":
    app = create_app()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True) 