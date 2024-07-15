#!/usr/bin/env python3
""" 12. Log stats"""

from pymongo import MongoClient


def log_stats():
    """
    Logs statistics about Nginx logs stored in MongoDB.
    """
    cl = MongoClient('mongodb://127.0.0.1:27017')
    nlc = cl.logs.nginx
    
    total_logs = nlc.count_documents({})
    get_requests = nlc.count_documents({"method": "GET"})
    post_requests = nlc.count_documents({"method": "POST"})
    put_requests = nlc.count_documents({"method": "PUT"})
    patch_requests = nlc.count_documents({"method": "PATCH"})
    delete_requests = nlc.count_documents({"method": "DELETE"})
    status_check_requests = nlc.count_documents({"method": "GET", "path": "/status"})
    
    print(f"{total_logs} logs")
    print("Methods:")
    print(f"\tmethod GET: {get_requests}")
    print(f"\tmethod POST: {post_requests}")
    print(f"\tmethod PUT: {put_requests}")
    print(f"\tmethod PATCH: {patch_requests}")
    print(f"\tmethod DELETE: {delete_requests}")
    print(f"{status_check_requests} status check")

if __name__ == "__main__":
    log_stats()
