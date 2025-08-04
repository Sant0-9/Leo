#!/usr/bin/env python3
"""
Leo AI Assistant - Full System Startup Script
Starts both backend and frontend servers concurrently
"""

import sys
import os
import subprocess
import threading
import time
from pathlib import Path

def start_backend():
    """Start backend server in a separate thread"""
    print("🧠 Starting Backend Server...")
    try:
        subprocess.run([sys.executable, "start_leo_backend.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Backend failed: {e}")
    except KeyboardInterrupt:
        print("🛑 Backend stopped")

def start_frontend():
    """Start frontend server in a separate thread"""
    print("⚛️ Starting Frontend Server...")
    time.sleep(3)  # Give backend a head start
    try:
        subprocess.run([sys.executable, "start_leo_frontend.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Frontend failed: {e}")
    except KeyboardInterrupt:
        print("🛑 Frontend stopped")

def main():
    """Main startup function"""
    print("🚀 Leo AI Assistant - Full System Startup")
    print("=" * 60)
    print("🧠 Backend: http://localhost:8000")
    print("⚛️ Frontend: http://localhost:3000")
    print("📚 API Docs: http://localhost:8000/docs")
    print("⚡ Press Ctrl+C to stop both servers")
    print("=" * 60)
    
    # Create threads for both servers
    backend_thread = threading.Thread(target=start_backend, daemon=True)
    frontend_thread = threading.Thread(target=start_frontend, daemon=True)
    
    try:
        # Start both servers
        backend_thread.start()
        frontend_thread.start()
        
        # Keep main thread alive
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Shutting down Leo AI Assistant...")
        print("⏳ Stopping servers...")
        # Threads will stop when main process exits
    
    print("✅ Leo AI Assistant stopped")

if __name__ == "__main__":
    main()