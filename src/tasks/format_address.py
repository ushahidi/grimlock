def run(data):
    address = ''

    if 'geo' not in data:
        return data

    component_keys = [ 
        'neighborhood', 
        'adminArea5',
        'adminArea4',
        'adminArea3',
        'adminArea2',
        'adminArea1'
    ]

    has_address = False
    if 'addressComponents' in data['geo']:
        for key in component_keys:
            if key in data['geo']['addressComponents']:
                has_address = True

    
    if has_address:
        address = build_address_from_components(data)
    elif 'locationIdentifiers' in data['geo']:
        address = build_address_from_identifiers(data)
    
    if address and len(address) > 0:
        if 'addressComponents' not in data['geo']:
            data['geo']['addressComponents'] = {}

        data['geo']['addressComponents']['formattedAddress'] = address


    if 'entities' not in data:
        data['entities'] = []

    if 'addressComponents' in data['geo']:
        for key in component_keys:
            if key in data['geo']['addressComponents'] and data['geo']['addressComponents'][key] not in data['entities']:
                data['entities'].append(data['geo']['addressComponents'][key])


    return data


def add_if_exists(obj, key):
    if key in obj and obj[key]:
        return obj[key] + ','

    return ''    


def build_address_from_components(data):
    components = data['geo']['addressComponents']

    if 'formattedAddress' in components and components['formattedAddress'] is not None and len(components['formattedAddress']) > 0:
        return components['formattedAddress']

    address = ""
    component_keys = [
        'streetNumber', 
        'streetName', 
        'neighborhood', 
        'adminArea5',
        'adminArea4',
        'adminArea3',
        'adminArea2',
        'adminArea1'
    ]

    for key in component_keys:
        address += add_if_exists(components, key)

    address = address[:-1]

    return address


def build_address_from_identifiers(data):
    """
    for key in ['authorLocationName', 'authorTimeZone']:
        if key in data['geo']['locationIdentifiers']:
            return data['geo']['locationIdentifiers'][key].strip()

    return ''
    """
    loc_id = data['geo']['locationIdentifiers']
    if 'authorTimeZone' in loc_id and loc_id['authorTimeZone']:
        return data['geo']['locationIdentifiers']['authorTimeZone']

    elif 'authorLocationName' in loc_id and loc_id['authorLocationName']:
        return data['geo']['locationIdentifiers']['authorLocationName']

    else:
        return ''