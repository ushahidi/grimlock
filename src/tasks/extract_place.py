# -*- coding: utf-8 -*-

# nltk to extract known entities
# fuzzy search for LOC entities against known city/region/country https://github.com/seatgeek/fuzzywuzzy
# build not-a-city-etc, city, region, country
# set properties on document

# hat tip http://stackoverflow.com/a/1342373/2367526
def remove_non_ascii(s): return "".join(i for i in s if ord(i)<128)

from nltk import metrics, stem, tokenize
 
stemmer = stem.PorterStemmer()
 
def normalize(s):
    words = tokenize.wordpunct_tokenize(s.lower().strip())
    return ' '.join([stemmer.stem(w) for w in words])
 
def fuzzy_match(s1, s2, max_dist=3):
    return metrics.edit_distance(normalize(s1), normalize(s2)) <= max_dist

import nltk
from newspaper import Article

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
        

# check if is in list of known countries
# check if in list of all known cities https://gist.github.com/fiorix/4592774

print places
print people
