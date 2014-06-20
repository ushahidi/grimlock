import requests
import urllib
from config import settings

def run(data):
    if 'image' not in data:
        return data

    url = 'http://access.alchemyapi.com/calls/url/URLGetRankedImageKeywords'
    params = {
        'apikey': settings.ALCHEMY_API_KEY,
        'url': data['image'],
        'imagePostMode': 'not-raw',
        'outputMode': 'json'
    }

    r = requests.get(url, params=params)
    r_data = r.json()

    for tag in r_data['imageKeywords']:
        if tag['text'] == 'person' and float(tag['score']) > 0.6:
            if 'tags' not in data:
                data['tags'] = []

            data['tags'].append({'name':'photo-person', 'confidence': float(tag['score'])})

    return data