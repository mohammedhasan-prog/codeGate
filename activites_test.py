# file_activity_test.py - Tests file monitoring
import os
import time

def suspicious_file_operations():
    """Patterns that should trigger security alerts"""
    
    # Rapid file creation (ransomware-like behavior)
    for i in range(100):
        filename = f"test_file_{i}.tmp"
        with open(filename, 'w') as f:
            f.write("test data")
        time.sleep(0.01)
    
    # File enumeration pattern
    for root, dirs, files in os.walk('.'):
        for file in files[:10]:  # Limit to prevent issues
            print(f"Found: {file}")
