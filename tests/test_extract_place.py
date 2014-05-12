# -*- coding: utf-8 -*-

import logging
requests_log = logging.getLogger("pycountry.db")
requests_log.setLevel(logging.WARNING)
from src.tasks import extract_place

def test():
    extract_place.setup()

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

    data['content'] = """ Perfect just Perfect! It's a perfect storm for Nairobi on a Friday evening! horrible traffic here is your cue to become worse @Ma3Route """

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

    data['content'] = "#مكتب_دمشق_الإعلامي | # Goobers | 10.5.2014 p for | Bombing was described as the deadliest targeting neighborhood Goobers from multiple sources since about the time amid violent clashes on the kafersoseh, he heard loud ambulance East of Damascus tanker dead and wounded troops.\nActivists said that several mortar shells landed in the area of the Abbasids along the lgobr."
    data['geo']['addressComponents'] = {
        'adminArea1': 'Syria'
    }

    data = extract_place.run(data)

    assert 'Damascus' in data['entities']
    assert data['geo']['addressComponents']['adminArea5'] == 'Damascus'

    data['geo']['addressComponents'] = {
        'adminArea1': 'Syria'
    }

    data['content'] = "# Flash _ Syria | | # Aleppo | | # Hayyan: wounding three children and two women, some in critical condition, after warplanes targeting the city's missile interstitial."
    data = extract_place.run(data)

    assert 'Aleppo' in data['entities']
    assert data['geo']['addressComponents']['adminArea5'] == 'Aleppo'
    