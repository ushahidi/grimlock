import logging
requests_log = logging.getLogger("pycountry.db")
requests_log.setLevel(logging.WARNING)
from src.tasks import extract_place

def test():
    data = {
        "remoteID": "291506692",
        "content": "Expelordeportindividuals",
        "source": "gdelt",
        "fromURL": "http://www.theage.com.au/world/taliban-attackers-mistake-armed-contractors-for-christian-daycare-workers-20140330-zqolw.html",
        "summary": "Expelordeportindividuals",
        "_id": "533a28bec906a78c36984a35",
        "license": "unknown",
        "language": {
            "code": "en",
            "name": "English",
            "nativeName": "English"
        },
        "tags": [
            {
                "name": "conflict",
                "_id": "533a28bec906a78c36984a36",
                "confidence": 1
            }
        ],
        "geo": {},
        "lifespan": "temporary",
        "createdAt": "2014-04-01T02: 47: 26.495Z",
        "__v": 0
    }

    data = extract_place.run(data)

    """ The article associated with data contains many references to Afghanistan
    and Kabul """
    
    assert 'addressComponents' in data['geo']
    assert data['geo']['addressComponents']['adminArea1'] == 'Afghanistan'
    assert data['geo']['addressComponents']['adminArea5'] == 'Kabul'

    """ Without a fromURL the extractor should use the content property """
    del data['geo']['addressComponents']
    del data['fromURL']

    data['content'] = """ Perfect just Perfect! It's a perfect storm for Nairobi on a 
    Friday evening! horrible traffic here is your cue to become worse @Ma3Route """

    data = extract_place.run(data)

    assert data['geo']['addressComponents']['adminArea1'] == 'Kenya'
    assert data['geo']['addressComponents']['adminArea5'] == 'Nairobi'

    """ Checking other branches in the logic. In theory same to above. """
    data['geo']['addressComponents'] = {
        'adminArea1': 'Kenya'
    }

    data = extract_place.run(data)

    assert data['geo']['addressComponents']['adminArea5'] == 'Nairobi'

    data['geo']['addressComponents'] = {
        'adminArea5': 'Nairobi'
    }

    data = extract_place.run(data)

    assert data['geo']['addressComponents']['adminArea1'] == 'Kenya'

    data['geo']['addressComponents'] = {
        'formattedAddress': ''
    }

    data = extract_place.run(data)

    assert data['geo']['addressComponents']['adminArea1'] == 'Kenya'
    assert data['geo']['addressComponents']['adminArea5'] == 'Nairobi'
    