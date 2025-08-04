#!/usr/bin/env python3
"""
Leo AI Assistant - Frontend Startup Script
Starts the React frontend development server
"""

import os
import sys
import subprocess
from pathlib import Path

def check_frontend_setup():
    """Check if frontend is properly set up"""
    frontend_dir = Path("frontend")
    
    if not frontend_dir.exists():
        print("❌ Frontend directory not found")
        return False
    
    # Check if node_modules exists
    node_modules = frontend_dir / "node_modules"
    if not node_modules.exists():
        print("📦 Installing frontend dependencies...")
        try:
            subprocess.run(["npm", "install"], cwd=frontend_dir, check=True)
            print("✅ Frontend dependencies installed")
        except subprocess.CalledProcessError:
            print("❌ Failed to install frontend dependencies")
            print("📝 Please run: cd frontend && npm install")
            return False
        except FileNotFoundError:
            print("❌ npm not found. Please install Node.js and npm")
            return False
    
    print("✅ Frontend setup complete")
    return True

def start_frontend():
    """Start the React development server"""
    frontend_dir = Path("frontend")
    
    print("⚛️ Starting Leo AI Assistant Frontend...")
    print("📡 Frontend will be available at: http://localhost:3000")
    print("🔗 Make sure backend is running at: http://localhost:8000")
    print("⚡ Press Ctrl+C to stop")
    print("-" * 50)
    
    try:
        # Start React development server
        subprocess.run(["npm", "start"], cwd=frontend_dir, check=True)
    except KeyboardInterrupt:
        print("\n🛑 Frontend server stopped")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting frontend: {e}")
    except FileNotFoundError:
        print("❌ npm not found. Please install Node.js and npm")

def main():
    """Main startup function"""
    print("🚀 Leo AI Assistant - Frontend Startup")
    print("=" * 50)
    
    # Check frontend setup
    if not check_frontend_setup():
        sys.exit(1)
    
    # Start frontend
    start_frontend()

if __name__ == "__main__":
    main()