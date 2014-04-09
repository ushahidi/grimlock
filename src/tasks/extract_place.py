# nltk to extract known entities
# fuzzy search for LOC entities against known city/region/country https://github.com/seatgeek/fuzzywuzzy
# build not-a-city-etc, city, region, country
# set properties on document

import os
import csv
import jellyfish
import nltk
import pycountry
from collections import Counter
from newspaper import Article

# hat tip http://stackoverflow.com/a/1342373/2367526
def remove_non_ascii(s): return "".join(i for i in s if ord(i)<128)
 
def fuzzy_match(s1, s2, max_dist=.8):
    return jellyfish.jaro_distance(s1, s2) >= max_dist

def correct_mispelling(s):
    cur_dir = os.path.dirname(os.path.realpath(__file__))
    with open(cur_dir+"/ISO3166ErrorDictionary.csv", "rb") as info:
        reader = csv.reader(info)
        for row in reader:
            if s in remove_non_ascii(row[0]):
                return row[2]

    return s

def is_a_country(s): 
    s = correct_mispelling(s)
    try:
        pycountry.countries.get(name=s)
        return True
    except KeyError, e:
        return False

def not_in_list_fuzzy(s, items):
    for item in items:
        if fuzzy_match(s, item):
            return False

    return True

def make_region_names(country_name):
    country_name = correct_mispelling(country_name)
    obj = pycountry.countries.get(name=country_name)
    regions = pycountry.subdivisions.get(country_code=obj.alpha2)

    return [r.name for r in regions]

"""
url = 'http://www.bbc.com/news/world-europe-26919928'
a = Article(url)
a.download()
a.parse()

text = nltk.word_tokenize(remove_non_ascii(a.text))
nes = nltk.ne_chunk(nltk.pos_tag(text))

places = []
people = []

for ne in nes:
    if len(ne) == 1:
        if ne.node == 'GPE' and ne[0][1] == 'NNP':
            places.append(ne[0][0])

        elif ne.node == 'PERSON':
            people.append(ne[0][0])

# Countries
countries = [place for place in places if is_a_country(place)]
not_countries = [place for place in places if not_in_list_fuzzy(place, countries)]

# Regions
matched_regions = {}
region_names = {}
for country in countries:
    region_names[country] = make_region_names(country)
    matched_regions[country] = []

for key,val in region_names.iteritems():
    for nc in not_countries:
        for v in val:
            if fuzzy_match(remove_non_ascii(nc), remove_non_ascii(v)):
                matched_regions[key].append(nc)

# Cities
all_regions = reduce(list.__add__, [val for val in matched_regions.values()], [])
possible_cities = [place for place in places if not_in_list_fuzzy(place, countries + all_regions)]
"""
import sqlite3

conn = sqlite3.connect(os.path.dirname(os.path.realpath(__file__)) + "/locs.db")
conn.text_factory = lambda x: unicode(x, 'utf-8', 'ignore')

with conn:
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS Cities")    
    cur.execute("CREATE TABLE Cities(Country TEXT, City TEXT, AccentCity TEXT, Region TEXT, Population INTEGER, Latitude REAL, Longitude REAL)")
    cur_dir = os.path.dirname(os.path.realpath(__file__))
    with open(cur_dir+"/worldcitiespop.txt", "rb") as info:
        reader = csv.reader(info)
        for row in reader:
            cur.execute("INSERT INTO Cities VALUES(?, ?, ?, ?, ?, ?, ?);", row)

        conn.commit()
        #conn.close()

"""
print matched_regions
print "---"
print possible_cities
print "---"
print Counter(countries).most_common()
"""

