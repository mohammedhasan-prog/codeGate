# test_kitchen_sink_stress.py
import os
import subprocess
import pickle
import yaml
import sqlite3

class UltimateStressTest:
    """Combines ALL types of issues in one nightmare class"""
    
    def __init__(self):
        # Hardcoded secrets
        self.secret_key = "sk-1234567890abcdef"
        self.db_pass = "admin123"
        
        # Unused variables
        unused1 = "never used"
        unused2 = 42
        unused3 = [1, 2, 3]
        
    def vulnerability_and_performance_disaster(self, user_data):
        """Combines security issues with performance problems"""
        
        # Security: Command injection
        os.system(f"grep '{user_data}' /etc/passwd")
        
        # Performance: Inefficient nested loops
        results = []
        for i in range(1000):  # O(n^3) complexity
            for j in range(100):
                for k in range(10):
                    # Security: SQL injection in loop
                    query = f"SELECT * FROM table WHERE id = {i} AND name = '{user_data}'"
                    
                    # Performance: String concatenation in loop
                    temp_str = ""
                    for char in str(i * j * k):
                        temp_str += char  # Should use join
                    
                    results.append(temp_str)
        
        # Security: Deserialization
        pickle.loads(user_data.encode())
        
        # Logic error: Assignment instead of comparison
        if user_data == "admin":  # Should be ==
            return "admin access"
        
        # Performance: Inefficient membership check
        if user_data in results:  # Large list, should use set
            return "found"
        
        return results
    
    def complex_branching_with_vulnerabilities(self, a, b, c, d, e):
        """High complexity AND security issues"""
        
        if a > 0:
            if b > 0:
                if c > 0:
                    if d > 0:
                        if e > 0:
                            # Security issue in complex branch
                            eval(f"result = {a} + {b} + {c} + {d} + {e}")
                        else:
                            subprocess.call(f"echo {e}", shell=True)
                    else:
                        os.system(f"ls {d}")
                else:
                    # Logic error with bitwise operator
                    if a > 0 & b > 0:  # Should be 'and'
                        pickle.loads(str(c).encode())
            else:
                # Unreachable code after this return
                return "early return"
                print("This will never execute")
                unused_var = "dead code variable"
        else:
            # Infinite loop potential
            counter = 0
            while counter < 100:
                if counter % 2 == 0:
                    counter += 1
                # counter never incremented when odd - infinite loop!
        
        # More dead code
        dead_function_call = self.unused_method()
        return "end"
    
    def unused_method(self):
        """Method that's never actually called"""
        return "I'm unused despite being 'called' in dead code"

# More unused functions at module level
def module_unused_function():
    return "Never called"

# Unused class
class UnusedComplexClass:
    def __init__(self):
        self.data = {}
    
    def process_data(self):
        # This method combines issues but is never called
        for key in self.data:
            os.system(f"echo {key}")  # Security issue in unused code
        
        return len(self.data)
