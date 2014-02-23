""" This is just an example. Inside the run method of a task you can do whatever 
you want. The only requirements are that your run method accepts a single 
argument - the structure to be transformed or augmented - and returns the 
transformed/augmented structure so that downstream tasks can make further 
modifications or update the document in the datastore. 

"""
def run(data):
    print "in example"
    data["hiphophoray"] = "ho, hey, ho"
    return data