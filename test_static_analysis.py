# Test file with various static analysis issues

import os
import sys
import json
import time

# Unused variable
unused_var = "this variable is never used"

# Unused function
def unused_function():
    """This function is never called."""
    return "unused"

# Function with high complexity
def complex_function(x, y, z):
    """This function has high cyclomatic complexity."""
    if x > 0:
        if y > 0:
            if z > 0:
                for i in range(x):
                    for j in range(y):
                        if i == j:
                            if z % 2 == 0:
                                print("even")
                            else:
                                print("odd")
                        else:
                            while i < 10:
                                i += 1
                                if i == 5:
                                    break
    return x + y + z

# Inefficient membership testing
def inefficient_search(items, target):
    """Using list for membership testing instead of set."""
    large_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10] * 100
    if target in large_list:  # Should use set
        return True
    return False

# Nested loops
def nested_loops_example():
    """Nested loops causing O(n²) complexity."""
    result = []
    for i in range(100):
        for j in range(100):
            result.append(i * j)
    return result

# Repeated computation in loop
def repeated_computation():
    """Inefficient repeated computation."""
    items = [1, 2, 3, 4, 5] * 20
    total = 0
    for i in range(len(items)):  # len() computed repeatedly
        total += items[i]
    return total

# Potential bitwise vs logical confusion
def bitwise_confusion(a, b):
    """Potential bitwise operator confusion."""
    # This might be intended as 'and' instead of '&'
    if a > 0 & b > 0:  # Should probably be 'and'
        return True
    return False

# Infinite loop
def infinite_loop_example():
    """Function with infinite loop."""
    while True:
        print("This will run forever")
        # No break statement

# Unreachable code
def unreachable_code_example():
    """Function with unreachable code."""
    x = 5
    return x
    print("This line is unreachable")  # Dead code
    x = 10

# Long function (over 50 lines)
def very_long_function():
    """This function is intentionally very long."""
    x = 1
    y = 2
    z = 3
    a = 4
    b = 5
    c = 6
    d = 7
    e = 8
    f = 9
    g = 10
    h = 11
    i = 12
    j = 13
    k = 14
    l = 15
    m = 16
    n = 17
    o = 18
    p = 19
    q = 20
    r = 21
    s = 22
    t = 23
    u = 24
    v = 25
    w = 26
    xx = 27
    yy = 28
    zz = 29
    aa = 30
    bb = 31
    cc = 32
    dd = 33
    ee = 34
    ff = 35
    gg = 36
    hh = 37
    ii = 38
    jj = 39
    kk = 40
    ll = 41
    mm = 42
    nn = 43
    oo = 44
    pp = 45
    qq = 46
    rr = 47
    ss = 48
    tt = 49
    uu = 50
    vv = 51
    ww = 52
    result = x + y + z + a + b + c + d + e + f + g + h + i + j + k + l + m + n + o + p + q + r + s + t + u + v + w + xx + yy + zz + aa + bb + cc + dd + ee + ff + gg + hh + ii + jj + kk + ll + mm + nn + oo + pp + qq + rr + ss + tt + uu + vv + ww
    return result

# Class with too many methods
class LargeClass:
    """Class with many methods."""
    def method1(self): pass
    def method2(self): pass
    def method3(self): pass
    def method4(self): pass
    def method5(self): pass
    def method6(self): pass
    def method7(self): pass
    def method8(self): pass
    def method9(self): pass
    def method10(self): pass
    def method11(self): pass
    def method12(self): pass
    def method13(self): pass
    def method14(self): pass
    def method15(self): pass
    def method16(self): pass
    def method17(self): pass
    def method18(self): pass
    def method19(self): pass
    def method20(self): pass
    def method21(self): pass
    def method22(self): pass

# Used function (should not be flagged as unused)
def used_function():
    """This function is actually used."""
    return "I'm used!"

# Main function that uses some of the defined functions
def main():
    """Main function."""
    result = complex_function(1, 2, 3)
    print(used_function())
    return result

if __name__ == "__main__":
    main()
