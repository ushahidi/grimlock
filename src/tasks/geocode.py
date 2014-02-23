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
    if 'formattedAddress' not in data['geo']['addressComponents']:
        return data

    url = 'http://dev.virtualearth.net/REST/v1/Locations/%s?key=%s' % (
        data['geo']['addressComponents']['formattedAddress'], settings.MAP_KEY) 
    
    r = requests.get(url)
    
    if r.status_code != 200:
        return data

    json_data = json.loads(r.text)

    if len(json_data['resourceSets']) == 0:
        return data

    if len(json_data['resourceSets'][0]['resources']) == 0:
        return data

    coords = json_data['resourceSets'][0]['resources'][0]['point']['coordinates']
    
    # API gives us lat,lng and we need lng,lat
    data['geo']['coordinates'] = coords[::-1]
    
    return data