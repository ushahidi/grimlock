from mongokit import Connection
from .models import Item


def get_connection():
    Item.__database__ = 'crisisnet'

    connection = Connection()
    connection.register([Item])

    return connection