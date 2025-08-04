#!/usr/bin/env python3
"""
Leo AI Assistant - Backend Startup Script
Starts the FastAPI backend server with proper configuration
"""

import sys
import os
import subprocess
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import fastapi
        import uvicorn
        import openai
        print("✅ Core dependencies found")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("📦 Please install requirements: pip install -r requirements.txt")
        return False

def check_environment():
    """Check if environment is properly configured"""
    env_file = Path(".env")
    if not env_file.exists():
        print("⚠️ .env file not found")
        print("📝 Create .env file with your OpenAI API key:")
        print("   OPENAI_API_KEY=your_key_here")
        return False
    
    # Load and check env
    from dotenv import load_dotenv
    load_dotenv()
    
    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key or openai_key == "your_openai_api_key_here":
        print("⚠️ OpenAI API key not configured")
        print("📝 Please set OPENAI_API_KEY in your .env file")
        return False
    
    print("✅ Environment configured")
    return True

def start_backend():
    """Start the FastAPI backend server"""
    from dotenv import load_dotenv
    load_dotenv()
    
    port = int(os.getenv("BACKEND_PORT", 8000))
    host = os.getenv("BACKEND_HOST", "localhost")
    
    print("🧠 Starting Leo AI Assistant Backend...")
    print(f"📡 Backend will be available at: http://{host}:{port}")
    print(f"🔌 WebSocket available at: ws://{host}:{port}/ws")
    print(f"📚 API docs available at: http://{host}:{port}/docs")
    print("⚡ Press Ctrl+C to stop")
    print("-" * 50)
    
    try:
        # Start the server using the backend_main.py file
        import uvicorn
        uvicorn.run("backend_main:app", host="0.0.0.0", port=port, reload=True)
    except KeyboardInterrupt:
        print("\n🛑 Backend server stopped")
    except Exception as e:
        print(f"❌ Error starting backend: {e}")

def main():
    """Main startup function"""
    print("🚀 Leo AI Assistant - Backend Startup")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check environment
    if not check_environment():
        print("⚠️ Environment issues detected, but starting anyway with mock data...")
    
    # Start backend
    start_backend()

if __name__ == "__main__":
    main()