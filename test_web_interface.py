#!/usr/bin/env python3
"""
Test the CodeGate Web Interface
"""

import requests
import json
import time

def test_web_interface():
    base_url = "http://localhost:5000"
    
    print("🧪 Testing CodeGate Web Interface...")
    
    # Test 1: Homepage
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("✅ Homepage accessible")
        else:
            print(f"❌ Homepage failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Homepage error: {e}")
        return
    
    # Test 2: Scan page
    try:
        response = requests.get(f"{base_url}/scan")
        if response.status_code == 200:
            print("✅ Scan page accessible")
        else:
            print(f"❌ Scan page failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Scan page error: {e}")
    
    # Test 3: History page
    try:
        response = requests.get(f"{base_url}/history")
        if response.status_code == 200:
            print("✅ History page accessible")
        else:
            print(f"❌ History page failed: {response.status_code}")
    except Exception as e:
        print(f"❌ History page error: {e}")
    
    # Test 4: API History endpoint
    try:
        response = requests.get(f"{base_url}/api/history")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ History API working - Found {data.get('total', 0)} scans")
        else:
            print(f"❌ History API failed: {response.status_code}")
    except Exception as e:
        print(f"❌ History API error: {e}")
    
    # Test 5: API Stats endpoint
    try:
        response = requests.get(f"{base_url}/api/history/stats")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Stats API working - Total scans: {data.get('total_scans', 0)}")
        else:
            print(f"❌ Stats API failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Stats API error: {e}")
    
    # Test 6: Test scan API with sample code
    print("\n🔍 Testing code analysis...")
    sample_code = '''import os

def vulnerable_function(user_input):
    # This contains a command injection vulnerability
    result = os.system(f"echo {user_input}")
    return result

def safe_function():
    return "Hello, World!"
'''
    
    try:
        scan_data = {
            "code": sample_code,
            "file_name": "test_vulnerability.py"
        }
        
        response = requests.post(
            f"{base_url}/api/scan", 
            json=scan_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            scan_id = result.get('scan_id')
            print(f"✅ Scan API working - Scan ID: {scan_id}")
            
            # Monitor the scan status
            print("📊 Monitoring scan progress...")
            for i in range(30):  # Wait up to 30 seconds
                time.sleep(1)
                status_response = requests.get(f"{base_url}/api/scan/{scan_id}/status")
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    status = status_data.get('status')
                    print(f"   Status: {status}")
                    
                    if status in ['completed', 'failed']:
                        if status == 'completed':
                            print("✅ Scan completed successfully!")
                        else:
                            print(f"❌ Scan failed: {status_data.get('error')}")
                        break
                else:
                    print(f"❌ Status check failed: {status_response.status_code}")
                    break
            else:
                print("⏰ Scan timeout - may still be running")
                
        else:
            print(f"❌ Scan API failed: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Scan API error: {e}")
    
    print("\n🎉 Web interface testing completed!")
    print(f"🌐 Access the web interface at: {base_url}")

if __name__ == "__main__":
    test_web_interface()
