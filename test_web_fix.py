#!/usr/bin/env python3
"""
Test the CodePreprocessor fix
"""

import requests
import json
import sys
import time

def test_web_scan():
    """Test the web scanning functionality"""
    
    # Test code with the stress2.py content
    test_code = '''# system_resource_attack.py - System resource exhaustion
import os
import sys
import tempfile
import threading
import subprocess
import time

class SystemResourceAttacker:
    def __init__(self):
        self.temp_dir = tempfile.gettempdir()
    
    def file_descriptor_exhaustion(self):
        """Exhaust file descriptors"""
        files = []
        try:
            while True:
                temp_file = tempfile.NamedTemporaryFile(delete=False)
                files.append(temp_file)
        except OSError:
            pass  # File descriptor limit reached
    
    def process_table_exhaustion(self):
        """Fill process table"""
        processes = []
        try:
            while True:
                # Create zombie processes
                p = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(1)"])
                processes.append(p)
        except OSError:
            pass
'''
    
    # Prepare the request
    url = "http://127.0.0.1:5000/api/scan"
    data = {
        "code": test_code,
        "file_name": "stress2.py"
    }
    
    print("🔍 Testing CodeGate Web Interface...")
    print(f"📡 Sending request to: {url}")
    
    try:
        # Send the scan request
        response = requests.post(url, json=data, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS: Web scan completed without CodePreprocessor error!")
            print(f"📊 Risk Score: {result.get('risk_score', 'N/A')}")
            print(f"🔍 Total Issues: {result.get('total_issues', 'N/A')}")
            print(f"🔒 Security Issues: {result.get('security_issues', 'N/A')}")
            print(f"⚡ Static Issues: {result.get('static_issues', 'N/A')}")
            print(f"⏱️ Execution Time: {result.get('execution_time', 'N/A')}s")
            return True
        else:
            print(f"❌ FAILED: HTTP {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ FAILED: Cannot connect to web interface. Is it running?")
        return False
    except requests.exceptions.Timeout:
        print("❌ FAILED: Request timed out")
        return False
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False

if __name__ == "__main__":
    print("CodeGate Web Interface Test")
    print("=" * 40)
    
    # Wait a moment for the server to be ready
    print("⏳ Waiting for web server to be ready...")
    time.sleep(3)
    
    success = test_web_scan()
    
    if success:
        print("\n🎉 CodePreprocessor fix SUCCESSFUL!")
        print("The web interface now works without the init argument error.")
    else:
        print("\n💥 CodePreprocessor fix FAILED!")
        print("The error is still present.")
    
    sys.exit(0 if success else 1)
