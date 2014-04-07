import langid

def has_lang(data):
    if 'language' in data:
        if data['language'] is None:
            return False

        if 'code' not in data['language']:
            return False

        if data['language']['code'] == '':
            return False

        return True

    return False

def run(data):
    if has_lang(data):
        return data

    code = langid.classify(data['content'])

    data['language'] = {
        'code': code[0]
    }

    return data