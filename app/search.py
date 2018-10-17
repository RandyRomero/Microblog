#!python3.6
# -*- coding: utf-8 -*-

# "Methods to work with Elasticsearch"

from flask import current_app


def add_to_index(index, model):
    """
    Add content of field from the db table to the Elasticsearch
    What field exactly is denoted in __searcheable__ attribute of passed db model

    :param index: name of table from database
    :param model: SQLAlchemy model (see app/models.py)
    :return: None
    """
    if not current_app.elasticsearch:
        return
    payload = {}
    for field in model.__searcheable__:
        payload[field] = getattr(model, field)
    current_app.elasticsearch.index(index=index, doc_type=index, id=model.id, body=payload)


def remove_from_index(index, model):
    """
    Remove item from Elasticsname of table from databaseearch that was removed from database
    :param index: name of table from database
    :param model: SQLAlchemy model (see app/models.py)
    :return: None
    """
    if not current_app.elasticsearch:
        return
    current_app.elasticsearch.delete(index=index, doc_type=index, id=model.id)


def query_index(index, query, page, per_page):
    """
    Method to search some text in Elasticsearch

    :param index: name of table from database
    :param query: text to search
    :param page: which page of results should we get back
    :param per_page: ow many posts per page with results there should be
    :return: ids of items that contain given text, and total number of found ids
    """
    if not current_app.elasticsearch:
        return [], 0
    search = current_app.elasticsearch.search(index=index, doc_type=index,
                                              body={'query': {'multi_match': {'query': query, 'fields': ['*']}},
                                                    'from': (page - 1) * per_page, 'size': per_page})
    ids = [int(hit['_id']) for hit in search['hits']['hits']]
    return ids, search['hits']['total']