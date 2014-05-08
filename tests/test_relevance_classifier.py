def test():
    from src.tasks import relevance_classifier
    import datetime

    data = {u'remoteID': u'132', u'language': {u'nativeName': u'English', u'code': u'en', u'name': u'English'}, u'license': u'unknown', u'tags': [], u'publishedAt': datetime.datetime(2011, 1, 5, 8, 0), u'summary': u'Traffic death: Pedestrian was knocked down by a matatu.', u'content': u'Traffic Accident: Pedestrian was knocked down by a matatu violence.', u'source': u'kenya-traffic-incidents-2011', u'__v': 0, u'lifespan': u'temporary', u'updatedAt': datetime.datetime(2014, 2, 23, 16, 8, 16, 832000), u'_id': '530a1cf010a84e0000392a65', u'geo': {u'addressComponents': {u'formattedAddress':'Yala,Siaya,Siaya,Kenya', u'adminArea1': u'Kenya', u'neighborhood': u'Yala', u'adminArea4': u'Siaya', u'adminArea5': u'Siaya'}}, u'createdAt': datetime.datetime(2014, 2, 23, 16, 8, 16, 831000)}
    data['searchText'] = data['content'] + ' ' + data['summary']

    run = relevance_classifier.setup()
    data = run(data)

    tag_names = [tag['name'] for tag in data['tags']]
    
    assert 'death' in tag_names
    assert 'conflict' in tag_names
    assert 'ethnic-violence' in tag_names