import requests
import json
from config import settings


def run(data):
    if 'geo' not in data or 'coords' not in data['geo'] or data['geo']['coords'] is None:
        return data

    include_entity_types = [
        'Address',
        'Neighborhood',
        'PopulatedPlace',
        'Postcode1',
        'AdminDivision1',
        'AdminDivision2',
        'CountryRegion'
    ]

    iet = ','.join(include_entity_types)
    latLng = ','.join([str(coord) for coord in data['geo']['coords'][::-1]])

    url = 'http://dev.virtualearth.net/REST/v1/Locations/%s?includeEntityTypes=%s&key=%s' % (
        latLng, iet, settings.MAP_KEY)

    r = requests.get(url)

    if r.status_code != 200:
        logger.error("Geocode error " + str(r.status_code))
        #print r.text
        return data

    try:
        json_data = r.json()
    except ValueError, e:
        logger.error("no json available from geocode")
        return data

    if len(json_data['resourceSets']) == 0:
        return data

    if len(json_data['resourceSets'][0]['resources']) == 0:
        return data

    address_data = json_data['resourceSets'][0]['resources'][0]['address']

    model_address_data = {}

    prop_map = {
        'addressLine': 'streetAddress',
        'adminDistrict': 'adminArea3',
        'adminDistrict2': 'adminArea4',
        'countryRegion': 'adminArea1',
        'locality': 'adminArea5',
        'postalCode': 'postalCode',
        'formattedAddress': 'formattedAddress'
    }

    def include_if_present(prop):
        if prop in address_data:
            model_address_data[prop_map[prop]] = address_data[prop]

    for key in prop_map:
        include_if_present(key)

    data['geo']['addressComponents'] = model_address_data

    return data