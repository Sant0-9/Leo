#!/usr/bin/env python3
"""
Leo AI Assistant - Main Entry Point
"""

import sys
import subprocess

def main():
    """Main entry point for Leo AI Assistant"""
    print("🧠 Leo AI Assistant")
    print("=" * 40)
    print("🚀 Full system: python3 start_leo_full.py")
    print("🔧 Backend only: python3 start_leo_backend.py")
    print("⚛️ Frontend only: python3 start_leo_frontend.py")
    print("=" * 40)
    
    try:
        choice = input("\nStart full system? (y/N): ").strip().lower()
        if choice in ['y', 'yes']:
            subprocess.run([sys.executable, "start_leo_full.py"])
        else:
            print("👋 Use the commands above when ready!")
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")

if __name__ == "__main__":
    main()