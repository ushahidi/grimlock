import os
os.environ['GRIMLOCK'] = 'test'
import logging
requests_log = logging.getLogger("pycountry.db")
requests_log.setLevel(logging.WARNING)

from src.tasks import (geocode, format_address, update_doc, identify_language, 
    add_default_values, reverse_geocode, extract_place, translate_content,
    relevance_classifier, extract_content, donation_classifier)

default_tasks = [
    add_default_values,
    extract_content,
    identify_language,
    translate_content,
    extract_place,
    #relevance_classifier,
    donation_classifier,
    format_address,
    geocode,
    reverse_geocode,
    update_doc
]

def test():
    import json
    import uuid
    from src.app import App, source
    from cn_search_py.connect import (setup_indexes, 
    get_connection as get_search_connection)
    from cn_search_py.collections import ItemCollection

    app = App("transform", pipeline_steps = default_tasks)

    random_id = str(uuid.uuid4())

    data = {
      'remoteID': random_id,
      'content': "U.S. aerial intervention against ISIS could give the upper hand to Iraqi security forces on the ground. But air power alone won't decide the battle against the jihadist group, says Karl Mueller. http://on.rand.org/yc6jH",
      'source': "facebook",
      'fromURL': "http://www.theage.com.au/world/taliban-attackers-mistake-armed-contractors-for-christian-daycare-workers-20140330-zqolw.html",
      'summary': "U.S. aerial intervention against ISIS could give the upper hand to Iraqi security forces on the ground. But air power alone won't decide the battle against the jihadist group, says Karl Mueller. http://on.rand.org/yc6jH",
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
        'addressComponents': {
          'formattedAddress': "Kabul, Kabol, Afghanistan"
        }
      },
      'lifespan': "temporary"
    }

    item = app.item_collection.make_model(data)
    saved = item.save(refresh=True)

    app.work(json.dumps({"id":str(saved['_id'])}))
    doc = source(app.item_collection, saved['_id'])()

    assert doc['remoteID'] == random_id
    assert 'Iraqi' in doc['entities']