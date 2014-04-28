import datetime

def setup(**kwargs):
    def run(doc):
        doc['updatedAt'] = datetime.datetime.utcnow()

        if 'item_collection' not in kwargs:
            raise 'update_doc task requires item_collection kwarg'
        
        ic = kwargs['item_collection']
        item = ic.make_model(doc)
        item.save()

        return item

    return run