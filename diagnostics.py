#-----------------------------------------------------------------------------
# Copyright 2013 Ra-el Peters
#-----------------------------------------------------------------------------
#    This file is part of pythonGameOfLife.
#
#    pythonGameOfLife is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    pythonGameOfLife is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with pythonGameOfLife.  If not, see <http://www.gnu.org/licenses/>.

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
            
