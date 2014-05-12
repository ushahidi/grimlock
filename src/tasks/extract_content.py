from newspaper import Article

def run(data):
    character_limit = 400

    if data['source'] in ['gdelt']:
        if 'content' in data and len(data['content']) < 100:
            if 'fromURL' not in data:
                return data
            try:
                a = Article(data['fromURL'])
                a.download()
                a.parse()
            except:
                return data

            if len(a.text) > character_limit:
                text = a.text[:character_limit] + '...'
            else:
                text = a.text

            data['content'] = text


    return data