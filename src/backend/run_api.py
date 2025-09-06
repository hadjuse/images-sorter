#!/usr/bin/env python3
"""
Script to start the Image Processing API
"""

import uvicorn
import os
import sys

# Add backend path to PYTHONPATH
backend_path = os.path.dirname(os.path.abspath(__file__))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

def main():
    """Start the API server"""
    print("Starting Image Processing API...")
    print("API will be available at: http://localhost:8000")
    print("Interactive documentation at: http://localhost:8000/docs")
    
    uvicorn.run(
        "api.api:app",
        host="127.0.0.1",
        port=8000,
        reload=True,  # Auto-reload in development
        log_level="info"
    )

if __name__ == "__main__":
    main()
