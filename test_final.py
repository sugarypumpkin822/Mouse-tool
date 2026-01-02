#!/usr/bin/env python3
"""
Final test of all three applications
"""

import subprocess
import sys

def test_app(name, command):
    """Test an application"""
    print(f"\n=== Testing {name} ===")
    try:
        result = subprocess.run([sys.executable, command, "--help"], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"[SUCCESS] {name} --help works")
        else:
            print(f"[FAILED] {name} --help failed")
            print(f"Error: {result.stderr[:200]}...")
    except subprocess.TimeoutExpired:
        print(f"[TIMEOUT] {name} --help timed out")
    except Exception as e:
        print(f"[CRASH] {name} --help crashed: {e}")

def main():
    """Test all applications"""
    print("Testing all three applications...")
    
    # Test server.py
    test_app("server.py", "server.py")
    
    # Test client.py
    test_app("client.py", "client.py")
    
    # Test main.py (minimal version)
    test_app("main_minimal.py", "main_minimal.py")
    
    print("\n=== Final Test Summary ===")
    print("Applications tested:")
    print("- server.py: Data synchronization server")
    print("- client.py: Data synchronization client") 
    print("- main_minimal.py: Main application with core features")
    print("\nAll tests completed")

if __name__ == "__main__":
    main()
