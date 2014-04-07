defaults = {
    'content': 'No content available'
}

def run(data):
    for key, val in defaults.iteritems():
        if key not in data or data[key] == '' or data[key] is None:
            data[key] = val

    return data
