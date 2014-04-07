import os
os.environ['GRIMLOCK'] = 'test'

def test():
    import json
    from src.app import App, source
    from src.cn_store_py.models import Item

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

    item = app.db.Item()

    for key in data:
        item[key] = data[key]
    
    item.save()

    app.work(json.dumps({"id":str(item['_id'])}))
    doc = source(app.db, item['_id'])()

    assert doc['geo']['addressComponents']['formattedAddress'] == "Kabul, Afghanistan"