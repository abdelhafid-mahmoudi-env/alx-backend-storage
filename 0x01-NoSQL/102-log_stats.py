#!/usr/bin/env python3
""" Log Stats """


from pymongo import MongoClient


def log_stats():
    client = MongoClient('mongodb://127.0.0.1:27017')
    logs_collection = client.logs.nginx

    # Total number of documents
    total_logs = logs_collection.count_documents({})
    print(f"{total_logs} logs")

    # HTTP Methods count
    methods = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']
    method_counts = {method: logs_collection.count_documents({'method': method}) for method in methods}
    print("Methods:")
    for method, count in method_counts.items():
        print(f"\t{method}: {count}")

    # GET /status count
    status_count = logs_collection.count_documents({'method': 'GET', 'path': '/status'})
    print(f"{status_count} status check")

if __name__ == "__main__":
    log_stats()
