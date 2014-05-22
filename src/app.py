import logging
import time
import sys
import json
from datetime import datetime
from qr import Queue
from config import settings
from pipeline import process
from tasks import (geocode, format_address, update_doc, identify_language, 
    add_default_values, reverse_geocode, extract_place, translate_content,
    relevance_classifier, extract_content)
from cn_store_py.connect import get_connection
from cn_search_py.connect import (setup_indexes, 
    get_connection as get_search_connection)
from cn_search_py.collections import ItemCollection

from bson import objectid

logger = logging.getLogger(__name__)


def source(item_collection, doc_id):
    """ Returns the function that will be called to feed data into the 
    pipeline. 

    """
    def get_doc():
        search_params = [
            {
                'field':'_id',
                'value': doc_id
            }
        ]
        #print "Processing doc " + str(id)
        doc = item_collection.get(search_params)
        return doc
        #return db.Item.find_one()

    return get_doc


def set_pipeline_steps(**kwargs):
    """ Define the order in which tasks should be executed in the pipeline. Each 
    task module should have a `run` method, which accepts a single argument 
    and either returns a value (probably a modified version of the object it 
    received) or saves to the database. 

    """
    steps = [
        add_default_values,
        extract_content,
        identify_language,
        translate_content,
        extract_place,
        relevance_classifier,
        format_address,
        geocode,
        reverse_geocode,
        update_doc
    ]
    
    return [mod.setup(**kwargs) if hasattr(mod, 'setup') else mod.run for mod in steps]


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
        self.search_db = get_search_connection()
        self.item_collection = ItemCollection(self.search_db)
        self.pipeline = set_pipeline_steps(item_collection=self.item_collection)


    def work(self, item):
        """ Feed jobs from the queue into the pipeline """
        try:
            data = json.loads(item)
            process(source(self.item_collection, data['id']), self.pipeline)
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
                time.sleep(1)
            except KeyboardInterrupt:
                logger.warn("Exiting grimlock")
                sys.exit()



def run_for_set(item_collection, start_date=None, end_date=None):
    if not start_date:
        raise Exception("run_for_set start_date is required") 

    pipeline = set_pipeline_steps(item_collection=item_collection)

    # No need to fail gracefully here. If the format is wrong go ahead and crash
    start = datetime.strptime(start_date, "%Y-%m-%d")
    search_val = start
    search_op = '>'
    end = None

    if end_date:
        end = datetime.strptime(end_date, "%Y-%m-%d")
        search_val = [start, end]
        search_op = 'between'

    search_params = [
        {
            'field':'updatedAt',
            'value': search_val,
            'op': search_op
        },
        {
            'field': 'source',
            'value': 'twitter'
        }
    ]

    def run(offset=0):
        docs = item_collection.find(search_params, offset=offset)
        print len(docs['docs'])
        for doc in docs['docs']:
            #pass
            process(lambda: doc, pipeline)

        offset += len(docs['docs'])
        if offset < docs['total']:
            run(offset=offset)
        else:
            print 'done'

    run()


def run_for_single(item_collection, doc_id):
    pipeline = set_pipeline_steps(item_collection=item_collection)
    process(source(item_collection, doc_id), pipeline)


if __name__ == "__main__":
    app = App("transform")
    args = sys.argv

    if len(args) > 1 and args[1] == '--fordates':

        if len(args) == 3:
            logger.info("Running with one arg: " + args[2])
            run_for_set(app.item_collection, start_date=args[2])

        elif len(args) == 4:
            logger.info("Running with two args: " + args[2] + ", " + args[3])
            run_for_set(app.item_collection, start_date=args[2], end_date=args[3])

    elif len(args) > 1 and args[1] == '--fordoc':
        run_for_single(app.item_collection, args[2])

    else:
        logger.info("Running process")
        app.start()

