import time
import sys

if sys.platform == "win32":
    # On Windows, the best timer is time.clock()
    getTimeInter = time.clock
else:
    # On most other platforms the best timer is time.time()
    getTimeInter = time.time

def getTime():
    return getTimeInter() * 1000.0

perfInfo = {}

def timeIt(name, thingToRun, *args, **krgs):
    start = getTime()
    result = thingToRun(*args, **krgs)
    end = getTime()
    perfInfo[name] = "{0:.4}".format(end - start)
    return result

def timeMe(original_function):
    def inner_function(*args, **kwargs):
        start = getTime()
        result = original_function(*args, **kwargs)
        end = getTime()
        itemName = "{0}.{1}".format(original_function.__module__, original_function.func_name)
        perfInfo[itemName] = "{0:.4}".format(end - start)
        return result
    inner_function.__doc__ = original_function.__doc__
    inner_function.__name__ = original_function.__name__    
    return inner_function
            
