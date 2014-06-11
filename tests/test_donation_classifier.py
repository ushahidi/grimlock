def test():
    from src.tasks import donation_classifier
    
    data = {
        'source': 'twitter',
        'content': "If you'd like to help with the #Sandy recovery, what's needed most is money, blood and volunteer labor: http://tnat.in/eTs77"
    }

    data = donation_classifier.run(data)
    tags = [tag['name'] for tag in data['tags']]

    assert 'donation' in tags
    assert 'donation-offer' in tags

    data = {
        'source': 'twitter',
        'content': "Heckuva Job Brownie criticizes Obama for responding to Hurricane Sandy so quickly. http://dlvr.it/2PgX64"
    }

    data = donation_classifier.run(data)

    assert 'donation' not in [tag['name'] for tag in data['tags']]
