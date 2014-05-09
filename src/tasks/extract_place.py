import geograpy

def run(data):
    if 'coords' in data['geo']:
        return data

    if 'fromURL' in data and data['source'] in ['gdelt']:
        pc = geograpy.get_place_context(url=data['fromURL'])

    elif 'searchText' in data and len(data['searchText']) > 0:
        if 'contentEnglish' in data:
            field = 'contentEnglish'
        else:
            field = 'searchText'
        pc = geograpy.get_place_context(text=data[field])

    else:
        return data

    if 'entities' not in data:
        data['entities'] = []

    for place in list(set(pc.places)):
        if place not in data['entities']:
            data['entities'].append(place)

    # starting from scratch with no location data
    if 'addressComponents' not in data['geo']:
        data['geo']['addressComponents'] = {}
        if pc.countries:
            # <place_type>_mentions are tuples ordered most > least, like 
            # [(Name1, 5), (Name2, 4)]. We'll assume the most mentioned is the 
            # most important.

            # now that we have a country, we only want regions/cities from 
            # within that country
            country = pc.country_mentions[0][0]
            data['geo']['addressComponents']['adminArea1'] = country

            data = region_city_for_country(data, country, pc)
        
        # without countries we're left to work our way back up the chain starting 
        # with city information
        else:
            if pc.cities:
                data['geo']['addressComponents']['adminArea5'] = pc.city_mentions[0][0]
                # now that we know we have a city, try to work backwards from 
                # here to get the country and region.
                build_from_city(data, pc)
    
    # we must already have some information about this place's location. use 
    # that in conjunction with the places returned by geograpy to fill in the 
    # gaps. 
    else:
        # top down from country
        if 'adminArea1' in data['geo']['addressComponents']:
            country = data['geo']['addressComponents']['adminArea1']
            
            # now that we have a a country, get regions cities that we might 
            # know about, assuming they are within that country
            data = region_city_for_country(data, country, pc)


        # try it with a city
        elif 'adminArea5' in data['geo'] and not pc.countries:
            # now that we know we have a city, try to work backwards from 
            # here to get the country and region.
            build_from_city(data, pc)

        # take your best shot at guessing the country and then working down from 
        # there.
        else:
            data = set_missing_country_region(data, pc)
            if 'adminArea1' in data['geo']['addressComponents']:
                country = data['geo']['addressComponents']['adminArea1']
                data = region_city_for_country(data, country, pc) 

            # We couldn't do anything with found country names, maybe we at least 
            # have a city mention.
            elif pc.cities:
                data['geo']['addressComponents']['adminArea5'] = pc.city_mentions[0][0]
                # now that we know we have a city, try to work backwards from 
                # here to get the country and region.
                build_from_city(data, pc)

    return data



def most_mentioned(place_names, place_mentions):
    for place in place_mentions:
        if place[0] in place_names:
            return place[0]


def mentioned_in_dict(place_name, country_dict):
    for key, val in country_dict.iteritems():
        if place_name in val:
            return key

    return None


def region_city_for_country(data, country, pc):
    # now that we country, only get regions and cities in that country
    if country in pc.country_regions and 'adminArea3' not in data['geo']['addressComponents']:
        data['geo']['addressComponents']['adminArea3'] = most_mentioned(
            pc.regions, pc.region_mentions)

    if country in pc.country_cities and 'adminArea5' not in data['geo']['addressComponents']:
        data['geo']['addressComponents']['adminArea5'] = most_mentioned(
            pc.cities, pc.city_mentions)

    return data


def set_missing_country_region(data, pc):
    if 'adminArea1' not in data['geo']['addressComponents'] and pc.countries:
        data['geo']['addressComponents']['adminArea1'] = pc.country_mentions[0][0]

    if 'adminArea3' not in data['geo']['addressComponents'] and pc.regions:
        data['geo']['addressComponents']['adminArea3'] = pc.region_mentions[0][0]

    return data


def build_from_city(data, pc):
    region_name = None

    components = data['geo']['addressComponents']
    if 'adminArea3' in components:
        region_name = components['adminArea3']
    elif 'adminArea2' in components:
        region_name = components['adminArea2']

    # get all cities matching this name
    possible_cities = geograpy.places.cities_for_name(data['geo']['addressComponents']['adminArea5'])
    actual_city = None

    # try to validate that of the cities returned, we have found one in 
    # a region that we're already aware of.
    if possible_cities:
        if region_name:
            for city in possible_cities:
                if city[6] == region_name:
                    actual_city = city
        
        # assuming we weren't able to match this city with a region we already 
        # knew about.
        if not actual_city and len(possible_cities) == 1:
            actual_city = possible_cities[0]
    else: 
        return set_missing_country_region(data, pc)

    # use city, country and region name from city record
    if actual_city:
        data['geo']['addressComponents']['adminArea5'] = actual_city[7]
        data['geo']['addressComponents']['adminArea1'] = actual_city[4]

        if 'adminArea3' not in data['geo']['addressComponents']:
            data['geo']['addressComponents']['adminArea3'] = actual_city[6]

    # oook. we're not very sure about the city, just set country/region
    else: 
        data = set_missing_country_region(data, pc)


    return data
