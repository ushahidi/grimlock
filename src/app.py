import redis
import sys
import json
from config import settings
from pipeline import process
from tasks import example, example2

def source(id):
    """ Returns the function that will be called to feed data into the 
    pipeline. 

    """
    def get_doc():
        return {
            'a': 'b',
            'c': 'd'
        }

    return get_doc


def set_pipeline_steps():
    """ Define the order in which tasks should be executed in the pipeline. Each 
    task module should have a `run` method, which accepts a single argument 
    and either returns a value (probably a modified version of the object it 
    received) or saves to the database. 

    """
    return [mod.run for mod in [example, example2]]


class App(object):
    """ Polls the queue and runs each received job through the processing
    pipeline.

    """
    def __init__(self, r, channels):
        """ Init redis pubsub and subscribe to the appropriate channels. 

        Args:
            r (redis.Redis): connected redis instance
            channels (array): string names of channels to which we should subscribe
        """
        self.redis = r
        self.pubsub = self.redis.pubsub()
        self.pubsub.subscribe(channels)


    def work(self, item):
        """ Feed jobs from the queue into the pipeline """

        try:
            data = json.loads(item['data'])
            process(source(data['id']), set_pipeline_steps())
        except:
            print "Problem!"

    
    def start(self):
        """ Listen to the channels we've subscribed to and pass retrieved items 
        to the worker 

        """
        print "Starting..."
        while True:
            try:
                for item in self.pubsub.listen():
                    self.work(item)
            except KeyboardInterrupt:
                print "Exiting..."
                sys.exit()



if __name__ == "__main__":
    r = redis.Redis()
    app = App(r, [settings.QUEUE_NAME])
    app.start()  

