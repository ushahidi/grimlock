import requests
import json
import logging

logger = logging.getLogger('grimlock')

def run(data):
    if data['source'] != 'twitter':
        return data

    if 'tags' not in data:
        data['tags'] = []


    url = 'http://knoesis-twit.cs.wright.edu/CrisisComputingAPI/classifyController'
    params = { 
        'text': data['content'],
        "classifyType": "all",
        "platform": "twitter",
        "timestamp": "2014-05-26 09:00:00",
        "location": "Dayton,OH",
        "latitude": 39.796931,
        "longitude": -84.27961,
        "msgId": "123456789"
    }
    headers = {'content-type': 'application/json'}

    r = requests.post(url, data=json.dumps(params), headers=headers)
    if r.status_code == 200:
        resp_json = r.json()

        if resp_json['donation_classification_probb'] > .5:
            data['tags'].append({
                'name': 'donation', 
                'confidence': resp_json['donation_classification_probb']
            })

            if resp_json["request_classification_probb"] > .2:
                data['tags'].append({
                    'name': 'donation-request', 
                    'confidence': resp_json['request_classification_probb']
                })

            if resp_json["offer_classification_probb"] > .2:
                data['tags'].append({
                    'name': 'donation-offer', 
                    'confidence': resp_json['offer_classification_probb']
                })
    else:
        logger.error("Donation classifier failed! " + str(r.status_code) + " ... " + r.text)


    return data