"""
Here lies all the code that isn't actually needed, but can be useful when debugging and thus I don't want to get rid of.
"""
from timeit import default_timer as timer
from math import log10


def measure_execution_time(foo):
    def wrapper(*args, **kwargs):
        start = timer()
        result = foo(*args, **kwargs)
        end = timer()
        if end - start > 2:
            print ("%s took %.2f seconds to execute!" % (foo.__name__, end-start))
        return result
    return wrapper


def log10wrapper(num):
    """
    :return: returns float_min instead of exception when given 0
    """
    if num == 0:
        return -float('inf')
    else:
        return log10(num)
