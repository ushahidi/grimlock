import geograpy

pc = geograpy.get_place_context(url='http://www.bbc.com/news/world-europe-26919928')

print pc.city_mentions
print pc.cities
print pc.country_cities
print pc.country_mentions
print pc.countries
print pc.region_mentions
print pc.country_regions
print pc.regions


