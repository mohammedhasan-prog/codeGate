# Vulnerable code for testing
import os
import subprocess
import sqlite3
import pickle
import yaml

# Command Injection
def command_injection(host):
    os.system(f'ping -c 4 {host}')

# SQL Injection
def sql_injection(user_id):
    db = sqlite3.connect('example.db')
    cursor = db.cursor()
    cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")
    user = cursor.fetchone()
    return user

# Deserialization
def unsafe_deserialization(data):
    return pickle.loads(data)

# Path Traversal
def path_traversal(filename):
    with open(f'/var/www/html/{filename}', 'r') as f:
        return f.read()

# Hardcoded Key
SECRET_KEY = "my_super_secret_key"
