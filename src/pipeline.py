import functools

def compose(*functions):
    """ As defined by our good friends at UnderscoreJS: Returns the composition of a 
    list of functions, where each function consumes the return value of the 
    function that follows. In math terms, composing the functions f(), g(), and h() 
    produces f(g(h())).

    One-liner borrowed from `Mathieu Larose <http://mathieularose.com/function-composition-in-python/>`_
    
    The important takeaway is that each function must accept the return value
    of the previous function. 

    >>> def func1(): return {'a': 'b'}
    >>> def func2(returnValueFromFunc1): return {'what': 'ever'} 

    :param functions:  As many functions as you want.
    
    """
    return functools.reduce(lambda f, g: lambda x: f(g(x)), functions)


def process(source, tasks):
    """ Compose a single function from the passed tasks, and feed the first function 
    in that chain the return value from source. 

    So...

    >>> task2(task1(source()))

    We're reversing the list of tasks so the consumer can pass in a list of 
    functions in preferred execution order.

    :param source: The function that will return the initial data for the pipeline
    :param tasks: A list of functions that will be called in sequence
    
    """
    compose(*tasks[::-1])(source())