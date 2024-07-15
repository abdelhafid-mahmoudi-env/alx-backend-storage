#!/usr/bin/env python3
""" 
MongoDB Operations with Python using pymongo 
Provides some stats about Nginx logs stored in MongoDB 
"""

from pymongo import MongoClient

if __name__ == "__main__":
    # Connect to MongoDB
    cli = MongoClient('mongodb://127.0.0.1:27017')
    
    # Access the nginx collection
    collect = cli.logs.nginx

    # Count total number of logs
    n_logs = collect.count_documents({})
    print(f'{n_logs} logs')

    # Count logs by HTTP methods
    methods = ["GET", "POST", "PUT", "PATCH", "DELETE"]
    print('Methods:')
    for method in methods:
        count = collect.count_documents({"method": method})
        print(f'\tmethod {method}: {count}')

    # Count GET requests to /status endpoint
    status_check = collect.count_documents(
        {"method": "GET", "path": "/status"}
    )
    print(f'{status_check} status check')
