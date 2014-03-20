def test():
    from src.tasks import format_address
    import datetime

    data = {u'remoteID': u'132', u'language': {u'nativeName': u'English', u'code': u'en', u'name': u'English'}, u'license': u'unknown', u'tags': [u'death', u'accident', u'road', u'injury'], u'publishedAt': datetime.datetime(2011, 1, 5, 8, 0), u'summary': u'Traffic Accident: Pedestrian was knocked down by a matatu.', u'content': u'Traffic Accident: Pedestrian was knocked down by a matatu.', u'source': u'kenya-traffic-incidents-2011', u'__v': 0, u'lifespan': u'temporary', u'updatedAt': datetime.datetime(2014, 2, 23, 16, 8, 16, 832000), u'_id': '530a1cf010a84e0000392a65', u'geo': {u'addressComponents': {u'adminArea1': u'Kenya', u'neighborhood': u'Yala', u'adminArea4': u'Siaya', u'adminArea5': u'Siaya'}}, u'createdAt': datetime.datetime(2014, 2, 23, 16, 8, 16, 831000)}

    data = format_address.run(data)

    assert 'formattedAddress' in data['geo']['addressComponents']
    assert data['geo']['addressComponents']['formattedAddress'] == 'Yala,Siaya,Siaya,Kenya'

    data2 = {u'remoteID': u'446712115228061696', u'language': {u'nativeName': u'English', u'code': u'en', u'name': u'English'}, u'license': u'unknown', u'tags': [], u'publishedAt': datetime.datetime(2014, 3, 20, 18, 17, 22), u'summary': u'What exactly has improved in Nairobi county ? Traffic lights? Water bill down? Security? Traffic...', u'content': u'What exactly has improved in Nairobi county ? Traffic lights? Water bill down? Security? Traffic jams? ....not very convinced...', u'source': u'twitter', u'__v': 0, u'lifespan': u'temporary', u'updatedAt': datetime.datetime(2014, 3, 20, 18, 18, 19, 1000), u'_id': '532b30eb7e93ef0000d6596f', u'geo': {u'locationIdentifiers': {u'authorTimeZone': u'Nairobi', u'authorLocationName': u'Nairobi - Kenya '}}, u'createdAt': datetime.datetime(2014, 3, 20, 18, 18, 18, 999000)}

    data2 = format_address.run(data2)

    assert 'formattedAddress' in data2['geo']['addressComponents']
    assert data2['geo']['addressComponents']['formattedAddress'] == 'Nairobi - Kenya'