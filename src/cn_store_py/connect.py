from mongokit import Connection
from .models import Item
from config import settings


def get_connection():
    Item.__database__ = settings.MONGO_DB

    connection = Connection(host=settings.MONGO_HOST)
    connection.register([Item])

    return connection