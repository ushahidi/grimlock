def run(data):
    components = data['geo']['addressComponents']

    if 'formattedAddress' in components and len(components['formattedAddress']) > 0:
        return data

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

    if len(address) > 0:
        data['geo']['addressComponents']['formattedAddress'] = address

    return data


def add_if_exists(obj, key):
    if key in obj:
        return obj[key] + ','

    return ''