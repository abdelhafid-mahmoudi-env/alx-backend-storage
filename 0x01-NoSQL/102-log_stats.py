#!/usr/bin/env python3
""" MongoDB Operations with Python using pymongo """
from pymongo import MongoClient


if __name__ == "__main__":
    """ Provides statistics about Nginx logs stored in MongoDB """
    # Connect to MongoDB
    client = MongoClient('mongodb://127.0.0.1:27017')
    
    # Access the nginx logs collection
    nginx_collection = client.logs.nginx

    # Count total logs
    total_logs = nginx_collection.count_documents({})
    print(f'Total logs: {total_logs}')

    # Count logs by HTTP methods
    http_methods = ["GET", "POST", "PUT", "PATCH", "DELETE"]
    print('Logs by HTTP methods:')
    for method in http_methods:
        method_count = nginx_collection.count_documents({"method": method})
        print(f'\t{method}: {method_count}')

    # Count GET requests to /status
    status_check_count = nginx_collection.count_documents(
        {"method": "GET", "path": "/status"}
    )
    print(f'GET requests to /status: {status_check_count}')

    # Find top 10 IPs with the most requests
    top_ips = nginx_collection.aggregate([
        {"$group":
            {
                "_id": "$ip",
                "count": {"$sum": 1}
            }
         },
        {"$sort": {"count": -1}},
        {"$limit": 10},
        {"$project": {
            "_id": 0,
            "ip": "$_id",
            "count": 1
        }}
    ])

    print("Top 10 IPs with most requests:")
    for top_ip in top_ips:
        ip_address = top_ip.get("ip")
        ip_count = top_ip.get("count")
        print(f'\t{ip_address}: {ip_count}')
