#!/usr/bin/env python3
""" Log stats - new version """
from pymongo import MongoClient


def mycheck_stats():
    """ provides some stats about Nginx logs stored in MongoDB:"""
    cli = MongoClient()
    collect = cli.logs.nginx

    numDocs = collect.count_documents({})
    print("{} logs".format(numDocs))
    print("Methods:")
    methods = ["GET", "POST", "PUT", "PATCH", "DELETE"]
    for method in methods:
        method_count = collect.count_documents({"method": method})
        print("\tmethod {}: {}".format(method, method_count))
    status = collect.count_documents({"method": "GET", "path": "/status"})
    print("{} status check".format(status))

    print("IPs:")

    ips = collect.aggregate([
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
    for ip in ips:
        count = ip.get("count")
        ip_address = ip.get("ip")
        print("\t{}: {}".format(ip_address, count))


if __name__ == "__main__":
    mycheck_stats()
