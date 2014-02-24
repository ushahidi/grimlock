import datetime

def run(doc):
    doc['updatedAt'] = datetime.datetime.utcnow()
    doc.save()