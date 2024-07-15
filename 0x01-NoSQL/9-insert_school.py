#!/usr/bin/env python3
"""
Module to insert a document into a MongoDB collection.
"""


def insert_school(mongo_collection, **kwargs):
    """
    Inserts a new document into a collection.

    :param mongo_collection.
    :param kwargs: The key-.
    :return: The ID of the newly inserted document.
    """
    new_document = mongo_collection.insert_one(kwargs)
    return new_document.inserted_id
