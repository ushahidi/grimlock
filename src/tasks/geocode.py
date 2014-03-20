""" This is just an example. Inside the run method of a task you can do whatever 
you want. The only requirements are that your run method accepts a single 
argument - the structure to be transformed or augmented - and returns the 
transformed/augmented structure so that downstream tasks can make further 
modifications or update the document in the datastore. 

"""

import requests
import json
from config import settings

def run(data):    
    if 'addressComponents' not in data['geo'] or 'formattedAddress' not in data['geo']['addressComponents']:
        return data

    url = 'http://dev.virtualearth.net/REST/v1/Locations/%s?key=%s' % (
        data['geo']['addressComponents']['formattedAddress'], settings.MAP_KEY) 
    
    r = requests.get(url)
    
    if r.status_code != 200:
        print "Geocode error " + str(r.status_code)
        print r.text
        return data

    json_data = r.json()

    if len(json_data['resourceSets']) == 0:
        return data

    if len(json_data['resourceSets'][0]['resources']) == 0:
        return data

    coords = json_data['resourceSets'][0]['resources'][0]['point']['coordinates']
    
    # API gives us lat,lng and we need lng,lat
    data['geo']['coords'] = {
        'type': 'Point',
        'coordinates': coords[::-1]
    }
    
    return data