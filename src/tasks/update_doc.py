import datetime

def setup(**kwargs):
    def run(data):
        data['updatedAt'] = datetime.datetime.utcnow()

        if 'entities' not in data:
          data['entities'] = []

        component_keys = [ 
            'neighborhood', 
            'adminArea5',
            'adminArea4',
            'adminArea3',
            'adminArea2',
            'adminArea1'
        ]

        if 'geo' in data and 'addressComponents' in data['geo']:
            for key in component_keys:
                if key in data['geo']['addressComponents'] and data['geo']['addressComponents'][key] not in data['entities']:
                    data['entities'].append(data['geo']['addressComponents'][key])

        if 'item_collection' not in kwargs:
            raise 'update_doc task requires item_collection kwarg'
        
        ic = kwargs['item_collection']

        item = ic.make_model(data)
        item.save(refresh=True)

        return item

    return run