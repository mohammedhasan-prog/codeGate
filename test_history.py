#!/usr/bin/env python3
"""
Test script for history functionality
"""
import asyncio
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, '/home/admin/Documents/codeGate/src')

from codegate.cli.commands import process_code
from codegate.utils.history import history_manager

async def test_history():
    print("Testing CodeGate history functionality...")
    
    # Test code 1 - with vulnerabilities
    test_code1 = """
import os
import subprocess

def dangerous_function(user_input):
    # This is vulnerable to command injection
    result = os.system(f"echo {user_input}")
    return result

def file_operation(filename):
    # This is vulnerable to path traversal
    with open(f"/data/{filename}", "r") as f:
        return f.read()
"""
    
    # Test code 2 - safer code
    test_code2 = """
import hashlib
import json

def safe_function(data):
    # This is relatively safe
    hash_value = hashlib.sha256(data.encode()).hexdigest()
    return hash_value

def process_data(data_dict):
    # Safe JSON processing
    return json.dumps(data_dict, indent=2)
"""
    
    print("\n1. Running first scan (vulnerable code)...")
    await process_code(test_code1, "/tmp/vulnerable_test.py")
    
    print("\n2. Running second scan (safer code)...")
    await process_code(test_code2, "/tmp/safe_test.py")
    
    print("\n3. Testing history retrieval...")
    recent_scans = history_manager.get_recent_scans(5)
    print(f"Found {len(recent_scans)} recent scans")
    
    for scan in recent_scans:
        print(f"  - Scan ID: {scan.scan_id}, Risk Score: {scan.risk_score}, Vulnerabilities: {scan.vulnerabilities_count}")
    
    print("\n4. Testing statistics...")
    stats = history_manager.get_statistics()
    print(f"Statistics: {stats}")
    
    print("\nHistory test completed!")

if __name__ == "__main__":
    asyncio.run(test_history())
