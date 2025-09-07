# resource_test.py - Tests CPU/Memory monitoring
import threading
import time
import os

def cpu_intensive_task():
    """Simulates high CPU usage - should be detectable"""
    while True:
        # Controlled CPU load with break condition
        for i in range(10000):
            pass
        time.sleep(0.001)  # Small break to prevent complete freeze

def memory_allocation():
    """Tests memory monitoring"""
    data = []
    for i in range(1000):  # Limited iterations
        data.append([0] * 10000)
        time.sleep(0.01)
    return data

# Your auditor should detect these patterns
threads = []
for i in range(2):  # Limited thread count
    t = threading.Thread(target=cpu_intensive_task)
    threads.append(t)
    t.start()
