import logging
from elasticsearch import Elasticsearch
from .models import Item
from .exceptions import DoesNotExist, MultipleObjectsReturned

logger = logging.getLogger(__name__)

class Collection(object):
    def make_model(self, data={}):
        return self.model(data, self)


    def _build_params(self, params):
        _params = []

        for param in params:
            if 'op' not in param:
                param['op'] = '='

            if param['op'] is '=':
                obj = {}
                obj[param['field']] = param['value']

                _params.append({ 'term': obj })

            elif param['op'] is 'between':
                obj = {}

                obj[param['field']] = {
                    'lte': param['value'][1],
                    'gte': param['value'][0]
                }

                _params.append({ 'range': obj })

            elif '>' in param['op'] or '<' in param['op']:
                obj = {}

                keys = {
                    '>': 'gt',
                    '<': 'lt',
                    '>=': 'gte',
                    '<=': 'lte'
                }

                key = keys[param['op']]

                obj[param['field']] = {}
                obj[param['field']][key] = param['value'] 

                _params.append({ 'range': obj })


        if len(_params) is 0:
            return _params[0]

        
        return {
            "and": _params
        }


    def _search(self, params, limit=100, offset=0):
        body = {
            "query": {
                "filtered" : {
                    "filter" : self._build_params(params)
                }
            }
        }

        kwargs = {
            'index': self.index,
            'doc_type': self.doc_type,
            'body': body,
            'size': limit
        }

        res = self.conn.search(**kwargs)

        return res

    
    def get(self, params):
        res = self._search(params)

        if res['hits']['total'] == 1:
            doc = res['hits']['hits'][0]['_source']
            doc['id'] = res['hits']['hits'][0]['_id']
            
            return doc

        if res['hits']['total'] == 0:
            raise DoesNotExist(
                "%s matching query does not exist. "
                "Lookup parameters were %s" %
                (self.model.__name__, params))

        raise MultipleObjectsReturned(
            "get() returned more than one %s -- it returned %s! "
            "Lookup parameters were %s" %
            (self.model.__name__, res['hits']['total'], params))


    def find(self, params, limit=100, offset=0):
        res = self._search(params)
        docs = []
        if res['hits']['total'] > 0:
            for hit in res['hits']['hits']:
                doc = hit['_source']
                doc['id'] = hit['_id']
                docs.append(doc)

        return {
            'total': res['hits']['total'],
            'docs': docs
        }


class ItemCollection(Collection):
    model = Item
    doc_type = 'item-type'
    index = 'item_alias'
    mapping = {
        'properties': {
            'geo': {
                'properties': {
                    'coords': {
                        'type': 'geo_point'
                    }
                }
            },
            'remoteID': {
                "type" : "string", 
                "index" : "not_analyzed"
            },
            'tags': {
                'properties': {
                    'name': {
                        'type': 'string',
                        'index': 'not_analyzed'
                    }
                }
            }
        }
    }


    def __init__(self, conn, index=None):
        self.conn = conn
        if index:
            self.index = index

