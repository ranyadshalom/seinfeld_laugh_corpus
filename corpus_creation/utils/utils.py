"""
Here lies all the code that isn't actually needed, but can be useful when debugging and thus I don't want to get rid of.
"""
from timeit import default_timer as timer


def measure_execution_time(foo):
    def wrapper(*args, **kwargs):
        start = timer()
        result = foo(*args, **kwargs)
        end = timer()
        if end - start > 2:
            print ("%s took %.2f seconds to execute!" % (foo.__name__, end-start))
        return result
    return wrapper
