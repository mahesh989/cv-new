#!/usr/bin/env python3
"""
Server Status Check Script

Check if the server is running and what errors might be occurring.
"""
import sys
import os
import subprocess
import requests
import time

def check_server_status():
    """Check server status and logs"""
    print("🔍 Server Status Check")
    print("=" * 50)
    
    # Check if server is running
    print("🌐 Checking server status...")
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("  ✅ Server is running and responding")
        else:
            print(f"  ⚠️  Server responded with status {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("  ❌ Server is not running or not accessible")
    except Exception as e:
        print(f"  ❌ Error checking server: {e}")
    
    # Check Docker containers
    print("\n🐳 Checking Docker containers...")
    try:
        result = subprocess.run(['docker', 'ps'], capture_output=True, text=True)
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            if len(lines) > 1:  # More than just header
                print("  ✅ Docker containers running:")
                for line in lines[1:]:
                    if line.strip():
                        print(f"    {line}")
            else:
                print("  ❌ No Docker containers running")
        else:
            print("  ❌ Docker not accessible")
    except Exception as e:
        print(f"  ❌ Docker error: {e}")
    
    # Check server logs
    print("\n📋 Checking server logs...")
    try:
        result = subprocess.run(['docker', 'logs', '--tail', '50', 'cv-magic-app'], capture_output=True, text=True)
        if result.returncode == 0:
            print("  📄 Recent server logs:")
            lines = result.stdout.strip().split('\n')
            for line in lines[-20:]:  # Last 20 lines
                if line.strip():
                    print(f"    {line}")
        else:
            print("  ❌ Could not get server logs")
    except Exception as e:
        print(f"  ❌ Log error: {e}")
    
    # Check if server is accessible from outside
    print("\n🌍 Checking external accessibility...")
    try:
        response = requests.get("http://cvagent.duckdns.org:8000/health", timeout=10)
        if response.status_code == 200:
            print("  ✅ Server accessible from outside")
        else:
            print(f"  ⚠️  External access returned status {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("  ❌ Server not accessible from outside")
    except Exception as e:
        print(f"  ❌ External access error: {e}")
    
    print("\n" + "=" * 50)
    print("🔧 Status Check Complete!")

if __name__ == "__main__":
    check_server_status()
