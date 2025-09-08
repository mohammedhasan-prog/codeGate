#!/usr/bin/env python3
"""
Test script for history CLI commands
"""
import sys
import json
from datetime import datetime

# Add the src directory to the Python path
sys.path.insert(0, '/home/admin/Documents/codeGate/src')

from codegate.utils.history import history_manager

def test_history_commands():
    print("Testing CodeGate history CLI commands...")
    
    # Create some mock history entries
    mock_reports = [
        {
            'file_path': '/tmp/vulnerable_test.py',
            'language': 'python',
            'risk_score': 85,
            'vulnerabilities': [
                {
                    'type': 'command_injection',
                    'severity': 'high',
                    'line_number': 6,
                    'code_snippet': 'os.system(f"echo {user_input}")',
                    'description': 'Command injection vulnerability',
                    'impact': 'Arbitrary command execution',
                    'remediation': 'Use subprocess with list arguments',
                    'cwe_id': 'CWE-78'
                }
            ],
            'summary': 'High risk vulnerabilities detected',
            'scan_duration': 1.5,
            'analysis_timestamp': datetime.now().isoformat(),
            'dependencies_analysis': {'detected_imports': ['os', 'subprocess']},
            'total_lines': 10
        },
        {
            'file_path': '/tmp/safe_test.py',
            'language': 'python',
            'risk_score': 15,
            'vulnerabilities': [],
            'summary': 'No significant vulnerabilities found',
            'scan_duration': 0.8,
            'analysis_timestamp': datetime.now().isoformat(),
            'dependencies_analysis': {'detected_imports': ['hashlib', 'json']},
            'total_lines': 8
        }
    ]
    
    # Save mock data to history
    scan_ids = []
    for report in mock_reports:
        scan_id = history_manager.save_scan(report)
        if scan_id:
            scan_ids.append(scan_id)
            print(f"✓ Saved scan with ID: {scan_id}")
    
    print(f"\n✓ Created {len(scan_ids)} test history entries")
    
    # Test recent scans
    print("\nTesting recent scans retrieval...")
    recent = history_manager.get_recent_scans(5)
    print(f"✓ Retrieved {len(recent)} recent scans")
    
    # Test statistics
    print("\nTesting statistics...")
    stats = history_manager.get_statistics()
    print(f"✓ Statistics: Total scans: {stats['total_scans']}, Avg risk: {stats['average_risk_score']}")
    
    # Test detailed scan retrieval
    if scan_ids:
        print(f"\nTesting detailed scan retrieval for ID: {scan_ids[0]}")
        details = history_manager.get_scan_details(scan_ids[0])
        if details:
            print(f"✓ Retrieved detailed scan: Risk score {details.entry.risk_score}")
        else:
            print("✗ Failed to retrieve scan details")
    
    print("\n✅ History functionality test completed successfully!")
    print("\nYou can now test the CLI commands:")
    print("  codegate")
    print("  > history")
    print("  > history --stats")
    print(f"  > history --details {scan_ids[0] if scan_ids else 'SCAN_ID'}")

if __name__ == "__main__":
    test_history_commands()
