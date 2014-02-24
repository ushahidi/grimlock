import time
import sys
import json
from qr import Queue
from config import settings
from pipeline import process
from tasks import geocode, format_address, update_doc
from cn_store_py.connect import get_connection
from bson import objectid

def source(db, id):
    """ Returns the function that will be called to feed data into the 
    pipeline. 

    """
    def get_doc():
        print "Processing doc " + str(id)
        return db.Item.one({'_id': objectid.ObjectId(id)})
        #return db.Item.find_one()

    return get_doc


def set_pipeline_steps():
    """ Define the order in which tasks should be executed in the pipeline. Each 
    task module should have a `run` method, which accepts a single argument 
    and either returns a value (probably a modified version of the object it 
    received) or saves to the database. 

    """
    steps = [
        format_address,
        geocode,  
        update_doc
    ]

    return [mod.run for mod in steps]

PIPELINE = set_pipeline_steps()


class App(object):
    """ Polls the queue and runs each received job through the processing
    pipeline.

    """
    def __init__(self, queue_name):
        """ Init redis pubsub and subscribe to the appropriate channels. 

        Args:
            r (redis.Redis): connected redis instance
            channels (array): string names of channels to which we should subscribe
        """
        self.queue = Queue(queue_name)
        self.queue.serializer = json
        self.db = get_connection()


    def work(self, item):
        """ Feed jobs from the queue into the pipeline """
        try:
            data = json.loads(item)
            process(source(self.db, data['id']), PIPELINE)
        except Exception, e:
            print "Problem! " + str(e)

    
    def start(self):
        """ Listen to the channels we've subscribed to and pass retrieved items 
        to the worker 

        """
        print "Starting..."
        while True:
            try:
                item = self.queue.pop()
                if item:
                    self.work(item)
                time.sleep(0.5)
            except KeyboardInterrupt:
                print "Exiting..."
                sys.exit()




if __name__ == "__main__":
    app = App("transform")
    app.start()  

