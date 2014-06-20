import requests
import urllib

def run(data):
    if 'image' not in data:
        return data

    url = 'http://access.alchemyapi.com/calls/url/URLGetRankedImageKeywords'
    params = {
        'apikey': '7acef4ecaf5f8574f867cb45404f63357a7c3a18',
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