#!/usr/bin/env python3
"""
Module to find schools by topic in a MongoDB collection.
"""


def schools_by_topic(mongo_collection, topic):
    """
    Returns the list of schools having a specific topic.

    :param mongo_collection: The MongoDB collection to query.
    :param topic: The topic to search for.
    :return: A cursor to the documents matching the topic.
    """
    return mongo_collection.find({"topics": topic})
