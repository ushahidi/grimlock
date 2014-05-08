import logging
import requests
from config import settings
import csv
import os
import jellyfish

def fuzzy_match(s1, s2, max_dist=.9):
    distance = jellyfish.jaro_distance(s1, s2)
    is_match = distance >= max_dist

    return is_match, distance


def setup(**kwargs):
    def get_tags(offset=0, total_retrieved=0, tags=[]):
        api_url = settings.API_URL
        api_key = settings.API_KEY

        url = api_url + '/system-tag?limit=200'
        headers = {'Authorization': 'Bearer ' + api_key}

        url = url + '&offset=' + str(offset)
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            json_data = r.json()
            tag_data = json_data['data']
            for tag in tag_data:
                tags.append(tag)

            total_retrieved += len(tag_data)
            if total_retrieved < json_data['total']:
                return get_tags(offset=total_retrieved, total_retrieved=total_retrieved, 
                    tags=tags)
            else:
                return tags
        else:
            return []

    tags = get_tags()

    
    def has_tag(tag_name, doc_tags):
        names = [tag['name'] for tag in doc_tags]
        return tag_name in names

    def tokenized_tag(tag):
        tag_names = tag['name'].split()

        tokens = []
            
        for tag_name in tag_names:
            tokens.append(tag_name)
            
            names = tag_name.split('-')
            for n in names:
                tokens.append(n)

        return tokens


    def run(data):
        if len(tags) == 0:
            logger.warn('No tags available for relevance_classifier')
            return data

        if 'contentEnglish' in data:
            field = 'contentEnglish'
        else:
            field = 'searchText'

        words = data[field].split()
        for tag in tags:
            if tag['name'] == 'conflict' or tag['name'] == 'disaster':
                continue
            tag_names = tokenized_tag(tag)

            for name in tag_names:
                for word in words:
                    if len(word) <= 3:
                        continue

                    is_match, distance = fuzzy_match(name.lower(), word.lower())

                    if is_match and not has_tag(tag['name'], data['tags']):
                        data['tags'].append({'name': tag['name'], 'confidence': distance})
                        for category in tag['categories']:
                            if not has_tag(category, data['tags']):
                                data['tags'].append({'name': category, 'confidence': 1})

        return data

    return run
