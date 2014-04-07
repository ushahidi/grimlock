def run(data):
    address = ''

    if not 'geo' in data:
        return data

    if 'addressComponents' in data['geo']:
        address = build_address_from_components(data)
    elif 'locationIdentifiers' in data['geo']:
        address = build_address_from_identifiers(data)
    
    if len(address) > 0:
        if 'addressComponents' not in data['geo']:
            data['geo']['addressComponents'] = {}

        data['geo']['addressComponents']['formattedAddress'] = address

    print data['geo']['addressComponents']

    return data


def add_if_exists(obj, key):
    if key in obj:
        return obj[key] + ','

    return ''


def build_address_from_components(data):
    components = data['geo']['addressComponents']

    if 'formattedAddress' in components and len(components['formattedAddress']) > 0:
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
    for key in ['authorLocationName', 'authorTimeZone']:
        if key in data['geo']['locationIdentifiers']:
            return data['geo']['locationIdentifiers'][key].strip()

    return ''