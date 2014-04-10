# nltk to extract known entities
# fuzzy search for LOC entities against known city/region/country https://github.com/seatgeek/fuzzywuzzy
# build not-a-city-etc, city, region, country
# set properties on document

import os
import csv
import jellyfish
import nltk
import pycountry
import sqlite3
from collections import Counter
from newspaper import Article

# hat tip http://stackoverflow.com/a/1342373/2367526
def remove_non_ascii(s): return "".join(i for i in s if ord(i)<128)
 

def fuzzy_match(s1, s2, max_dist=.8):
    return jellyfish.jaro_distance(s1, s2) >= max_dist


class Extractor(object):
    def __init__(self, text=None, url=None):
        if not text and not url:
            raise Exception('text or url is required')

        self.text = text
        self.url = url
        self.places = []
        self.people = []

    
    def set_text(self):
        if not self.text and self.url:
            a = Article(self.url)
            a.download()
            a.parse()
            self.text = a.text


    def find_entities(self):
        self.set_text()

        text = nltk.word_tokenize(remove_non_ascii(self.text))
        nes = nltk.ne_chunk(nltk.pos_tag(text))

        for ne in nes:
            if len(ne) == 1:
                if ne.node == 'GPE' and ne[0][1] == 'NNP':
                    self.places.append(ne[0][0])

                elif ne.node == 'PERSON':
                    self.people.append(ne[0][0])



class PlaceContext(object):
    def __init__(self, place_names, db_file=None):
        db_file = db_file or os.path.dirname(os.path.realpath(__file__)) + "/locs.db"
        self.conn = sqlite3.connect(db_file)
        self.conn.text_factory = lambda x: unicode(x, 'utf-8', 'ignore')
        self.places = place_names


    def populate_db(self):
        cur = self.conn.cursor()
        cur.execute("DROP TABLE IF EXISTS cities")    

        cur.execute("CREATE TABLE cities(geoname_id INTEGER, continent_code TEXT, continent_name TEXT, country_iso_code TEXT, country_name TEXT, subdivision_iso_code TEXT, subdivision_name TEXT, city_name TEXT, metro_code TEXT, time_zone TEXT)")
        cur_dir = os.path.dirname(os.path.realpath(__file__))
        with open(cur_dir+"/GeoLite2-City-Locations.csv", "rb") as info:
            reader = csv.reader(info)
            for row in reader:
                cur.execute("INSERT INTO cities VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?);", row)

            conn.commit()


    def db_has_data(self):
        cur = self.conn.cursor()

        cur.execute("SELECT Count(*) FROM sqlite_master WHERE name='cities';")
        data = cur.fetchone()[0]

        if data > 0:
            cur.execute("SELECT Count(*) FROM cities")
            data = cur.fetchone()[0]
            return data > 0

        return False

    
    def correct_country_mispelling(self, s):
        cur_dir = os.path.dirname(os.path.realpath(__file__))
        with open(cur_dir+"/ISO3166ErrorDictionary.csv", "rb") as info:
            reader = csv.reader(info)
            for row in reader:
                if s in remove_non_ascii(row[0]):
                    return row[2]

        return s

    
    def is_a_country(self, s): 
        s = self.correct_country_mispelling(s)
        try:
            pycountry.countries.get(name=s)
            return True
        except KeyError, e:
            return False

    
    def get_region_names(self, country_name):
        country_name = self.correct_country_mispelling(country_name)
        obj = pycountry.countries.get(name=country_name)
        regions = pycountry.subdivisions.get(country_code=obj.alpha2)

        return [r.name for r in regions]


    def set_countries(self):
        countries = [self.correct_country_mispelling(place) 
            for place in self.places if self.is_a_country(place)]

        self.country_mentions = Counter(countries).most_common()
        self.countries = list(set(countries))


    def set_regions(self):
        regions = []
        self.country_regions = {}
        region_names = {}
        
        if not self.countries:
            self.set_countries()

        def region_match(place_name, region_name):
            return fuzzy_match(remove_non_ascii(place_name), 
                remove_non_ascii(region_name))

        def is_region(place_name, region_names):
            return filter(lambda rn: region_match(place_name, rn), region_names)

        for country in self.countries:
            region_names = self.get_region_names(country)
            matched_regions = [p for p in self.places if is_region(p, region_names)]

            regions += matched_regions
            self.country_regions[country] = matched_regions

        self.region_mentions = Counter(regions).most_common()
        self.regions = list(set(regions))


    def set_cities(self):
        self.cities = []
        self.possible_cities = []
        self.country_cities = {}
        self.address_strings = []

        if not self.countries:
            self.set_countries()

        if not self.regions:
            self.set_regions()

        if not self.db_has_data():
            self.populate_db()

        cur = self.conn.cursor()
        cur.execute("SELECT * FROM cities WHERE city_name IN (" + ",".join("?"*len(self.places)) + ")", self.places)
        rows = cur.fetchall()

        for row in rows:
            country = None
            
            try:
                country = pycountry.countries.get(alpha2=row[3])
            except KeyError, e:
                pass

            city_name = row[7]
            region_name = row[6]

            if city_name not in self.possible_cities:
                self.possible_cities.append(city_name)

            if country and country.name in self.countries:
                if city_name not in self.cities:
                    self.cities.append(city_name)

                if country.name not in self.country_cities:
                    self.country_cities[country.name] = []
                
                if city_name not in self.country_cities[country.name]:
                    self.country_cities[country.name].append(city_name)

                    if country.name in self.country_regions and region_name in self.country_regions[country.name]:
                        self.address_strings.append(city_name + ", " + region_name + ", " + country.name)


        all_cities = [p for p in self.places if p in self.cities]
        self.city_mentions = Counter(all_cities).most_common()




e = Extractor(url='http://www.bbc.com/news/world-europe-26919928')
e.find_entities()

pc = PlaceContext(e.places)
pc.set_countries()
pc.set_regions()
pc.set_cities()

print pc.city_mentions
print pc.cities
print pc.country_cities
print pc.country_mentions
print pc.countries
print pc.region_mentions
print pc.regions


