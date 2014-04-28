import os
os.environ['GRIMLOCK'] = 'test'
import logging
requests_log = logging.getLogger("pycountry.db")
requests_log.setLevel(logging.WARNING)

def test():
    import json
    from src.app import App, source
    from cn_search_py.connect import (setup_indexes, 
    get_connection as get_search_connection)
    from cn_search_py.collections import ItemCollection

    app = App("transform")

    data = {
      'remoteID': "291506692",
      'content': "Expel or deport individuals",
      'source': "gdelt",
      'fromURL': "http://www.theage.com.au/world/taliban-attackers-mistake-armed-contractors-for-christian-daycare-workers-20140330-zqolw.html",
      'summary': "Expel or deport individuals",
      'license': "unknown",
      'language': {
        'code': "en",
        'name': "English",
        'nativeName': "English"
      },
      'tags': [
        {
          'name': "Christianity",
          'confidence': 1
        },
        {
          'name': "deportation",
          'confidence': 1
        },
        {
          'name': "conflict",
          'confidence': 1
        }
      ],
      'geo': {
        'coords': [
          69.1833,
          34.5167
        ],
        'addressComponents': {
          'formattedAddress': "Kabul, Kabol, Afghanistan"
        }
      },
      'lifespan': "temporary"
    }

    item = app.item_collection.make_model(data)
    saved = item.save()

    app.work(json.dumps({"id":str(saved['_id'])}))
    doc = source(app.item_collection, saved['_id'])()

    print doc

    assert doc['geo']['addressComponents']['formattedAddress'] == "Kabul, Afghanistan"