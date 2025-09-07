# network_test.py - Tests network monitoring
import socket
import threading
import time

def network_scanner():
    """Simulates port scanning behavior"""
    target = "127.0.0.1"  # Only scan localhost
    ports = [22, 80, 443, 8080, 3389]
    
    for port in ports:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((target, port))
            sock.close()
            time.sleep(0.1)
        except:
            pass
