import logging
import time
import sys
import json
from datetime import datetime
from qr import Queue
from config import settings
from pipeline import process
from tasks import (geocode, format_address, update_doc, identify_language, 
    add_default_values, reverse_geocode)
from cn_store_py.connect import get_connection
from bson import objectid

logger = logging.getLogger(__name__)

def source(db, id):
    """ Returns the function that will be called to feed data into the 
    pipeline. 

    """
    def get_doc():
        #print "Processing doc " + str(id)
        doc = db.Item.one({'_id': objectid.ObjectId(id)})
        return doc
        #return db.Item.find_one()

    return get_doc


def set_pipeline_steps():
    """ Define the order in which tasks should be executed in the pipeline. Each 
    task module should have a `run` method, which accepts a single argument 
    and either returns a value (probably a modified version of the object it 
    received) or saves to the database. 

    """
    steps = [
        add_default_values,
        identify_language,
        format_address,
        geocode,
        reverse_geocode,  
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
        self.queue = Queue(queue_name, host=settings.REDIS_HOST, 
            port=settings.REDIS_PORT, password=settings.REDIS_PASSWORD)
        self.queue.serializer = json
        self.db = get_connection()


    def work(self, item):
        """ Feed jobs from the queue into the pipeline """
        try:
            data = json.loads(item)
            process(source(self.db, data['id']), PIPELINE)
        except Exception, e:
            import traceback
            logger.error("Problem! " + str(e))
            logger.error(traceback.format_exc())
        #data = json.loads(item)
        #process(source(self.db, data['id']), PIPELINE)

    
    def start(self):
        """ Listen to the channels we've subscribed to and pass retrieved items 
        to the worker 

        """
        logger.warn("Starting grimlock")
        while True:
            try:
                item = self.queue.pop()
                if item:
                    self.work(item)
                time.sleep(0.2)
            except KeyboardInterrupt:
                logger.warn("Exiting grimlock")
                sys.exit()



def run_for_set(db, start_date=None, end_date=None):
    if not start_date:
        raise Exception("run_for_set start_date is required") 

    # No need to fail gracefully here. If the format is wrong go ahead and crash
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = None

    if end_date:
        end = datetime.strptime(start_date, "%Y-%m-%d")

    query_params = {
        'createdAt': { '$gte': start }
    }

    if end:
        query_params['createdAt'] = { '$lte': end }

    docs = db.Item.find(query_params)
    
    for doc in docs:
        process(lambda: doc, PIPELINE)



if __name__ == "__main__":
    app = App("transform")
    args = sys.argv

    if len(args) == 1:
        logger.info("No args, running process")
        app.start()

    elif len(args) == 2:
        logger.info("Running with one arg: " + args[1])
        run_for_set(db=app.db, start_date=args[1])

    elif len(args) == 3:
        logger.info("Running with two args: " + args[2])
        run_for_set(db=app.db, start_date=args[1], end_date=args[2])

