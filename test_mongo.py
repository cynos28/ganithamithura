import os
import certifi
from pymongo import MongoClient

MONGODB_URL = "mongodb+srv://nethmi:nethmi@itpm.nbiremo.mongodb.net/"

print("--- Test 1: certifi ---")
try:
    client = MongoClient(MONGODB_URL, tlsCAFile=certifi.where(), serverSelectionTimeoutMS=5000)
    client.admin.command('ping')
    print("Certifi ping successful")
except Exception as e:
    print(f"Failed: {e}")

print("--- Test 2: tlsAllowInvalidCertificates=True without tls=True ---")
try:
    client = MongoClient(MONGODB_URL, tlsAllowInvalidCertificates=True, serverSelectionTimeoutMS=5000)
    client.admin.command('ping')
    print("Insecure ping successful")
except Exception as e:
    print(f"Failed: {e}")

print("--- Test 3: tls=True, tlsAllowInvalidCertificates=True ---")
try:
    client = MongoClient(MONGODB_URL, tls=True, tlsAllowInvalidCertificates=True, serverSelectionTimeoutMS=5000)
    client.admin.command('ping')
    print("Insecure tls=True ping successful")
except Exception as e:
    print(f"Failed: {e}")
