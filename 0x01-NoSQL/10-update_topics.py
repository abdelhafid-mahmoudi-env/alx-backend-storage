#!/usr/bin/env python3
"""
Module to change school topics in a MongoDB collection.
"""


def update_topics(mongo_collection, name, topics):
    """
    Changes all topics of school documents based on the name.

    :param mongo_collection: The MongoDB collection to update.
    :param name: The name of the school documents to update.
    :param topics: The new list of topics to set.
    :return: None
    """
    mongo_collection.update_many({"name": name}, {"$set": {"topics": topics}})
