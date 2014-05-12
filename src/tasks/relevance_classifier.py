import logging
import requests
from config import settings
import csv
import os
import jellyfish
from .data import word_tag_map

def fuzzy_match(s1, s2, max_dist=.9):
    try:
        distance = jellyfish.jaro_distance(s1, s2)
        is_match = distance >= max_dist
    except:
        is_match = False
        distance = 0

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

        #data['tags'] = []
        if 'tags' in data:
            found_tags = [_ for _ in data['tags']]
        else:
            found_tags = []


        def add_tag(tag):
            if len(found_tags) > 20:
                return

            found_tags.append({'name': tag['name'], 'confidence': 1})
            if 'categories' in tag:
                for category in tag['categories']:
                    if category in ['disaster','crisis'] and not has_tag(category, found_tags):
                        found_tags.append({'name': category, 'confidence': 1})


        if 'contentEnglish' in data:
            combined_text = data['contentEnglish']
        else:
            combined_text = data['searchText']

        for keyword in word_tag_map.keywords:
            if keyword['word'] in combined_text:
                for tag in keyword['tags']:
                    if not has_tag(tag, found_tags):
                        add_tag({'name': tag})


        for tag in tags:
            if tag['name'] == 'conflict' or tag['name'] == 'disaster':
                continue

            if ' ' + tag['name'].replace('-', ' ').lower() + ' ' in combined_text and not has_tag(tag['name'], found_tags):
                add_tag(tag)


            if 'entities' in data:
                for entity in data['entities']:
                    is_match, distance = fuzzy_match(entity.lower(), tag['name'].lower()) 
                    if is_match and not has_tag(tag['name'], found_tags):
                        add_tag(tag)

        
        if len(found_tags) > 0:
            if 'tags' not in data:
                data['tags'] = found_tags
            else:
                for tag in found_tags:
                    if not has_tag(tag['name'], data['tags']):
                        data['tags'].append(tag)


        """
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
        """

        return data

    return run
