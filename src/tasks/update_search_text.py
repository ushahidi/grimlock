def run(data):
    if 'content' in data:
        data['searchText'] = data['content']

    if 'summary' in data:
        data['searchText'] += ' ' + data['summary']

    if 'contentEnglish' in data:
        data['searchText'] += ' ' + data['contentEnglish']

    if 'entities' in data:
        data['searchText'] += ' ' + ' '.join(data['entities'])

    if 'tags' in data:
        data['searchText'] += ' ' + ' '.join([tag['name'] for tag in data['tags']])

    
    return data