from mongokit import Document
#from pymongo import objectid
import datetime

class Item(Document):
    __collection__ = 'items'

    structure = {
        'createdAt': datetime.datetime,
        'udpatedAt': datetime.datetime,
        'remoteID': basestring,
        'activeUntil': datetime.datetime,
        'lifespan': basestring,
        'content': basestring,
        'summary': basestring,
        'image': basestring,
        'geo': {
            'namedPlaces': [basestring],
            'coordinates': [float],
            'accuracy': int,
            'granularity': basestring,
            'locationIdentifiers': {
                'authorLocationName': basestring,
                'authorTimeZone': basestring
            }
        },
        'tags': [basestring],
        'language': {
            'code': basestring,
            'name': basestring,
            'nativeName': basestring
        },
        'sourceID': None,
        'license': basestring
    }
    required_fields = ['remoteID', 'lifespan']
    default_values = {
        'license': 'unknown',
        'lifespan': 'temporary',
        'createdAt': datetime.datetime.utcnow
    }