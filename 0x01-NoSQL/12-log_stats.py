#!/usr/bin/env python3
""" log stats for client"""


from pymongo import MongoClient


def log_stats():
    """ log_stats.
    """
    client = MongoClient('mongodb://127.0.0.1:27017')
    log_mycollection = client.logs.nginx
    total = log_mycollection.count_documents({})
    get = log_mycollection.count_documents({"method": "GET"})
    post = log_mycollection.count_documents({"method": "POST"})
    put = log_mycollection.count_documents({"method": "PUT"})
    patch = log_mycollection.count_documents({"method": "PATCH"})
    delete = log_mycollection.count_documents({"method": "DELETE"})
    path = log_mycollection.count_documents(
        {"method": "GET", "path": "/status"})
    print(f"{total} logs")
    print("Methods:")
    print(f"\tmethod GET: {get}")
    print(f"\tmethod POST: {post}")
    print(f"\tmethod PUT: {put}")
    print(f"\tmethod PATCH: {patch}")
    print(f"\tmethod DELETE: {delete}")
    print(f"{path} status check")


if __name__ == "__main__":
    log_stats()
