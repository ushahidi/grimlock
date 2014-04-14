""" This is just an example. Inside the run method of a task you can do whatever 
you want. The only requirements are that your run method accepts a single 
argument - the structure to be transformed or augmented - and returns the 
transformed/augmented structure so that downstream tasks can make further 
modifications or update the document in the datastore. 

"""

import requests
import json
import logging
from config import settings

logger = logging.getLogger(__name__)

def run(data):    
    # We can only geocode if we have an address
    if 'geo' not in data or 'addressComponents' not in data['geo'] or 'formattedAddress' not in data['geo']['addressComponents']:
        return data

    # Assumption is that provided coords are accurate enough (if they exist)
    if 'coords' in data['geo']:
        return data

    url = 'http://dev.virtualearth.net/REST/v1/Locations/%s?key=%s' % (
        data['geo']['addressComponents']['formattedAddress'], settings.MAP_KEY) 
    
    r = requests.get(url)
    
    if r.status_code != 200:
        logger.error("Geocode error " + str(r.status_code))
        #print r.text
        return data

    try:
        json_data = r.json()
    except ValueError, e:
        logger.error("no json available from geocode")
        return data

    if len(json_data['resourceSets']) == 0:
        return data

    if len(json_data['resourceSets'][0]['resources']) == 0:
        return data

    coords = json_data['resourceSets'][0]['resources'][0]['point']['coordinates']
    
    # API gives us lat,lng and we need lng,lat
    data['geo']['coords'] = coords[::-1]
    
    return data