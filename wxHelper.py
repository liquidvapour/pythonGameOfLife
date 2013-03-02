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

def GetKeyName(keycode):
    keyname = ""
    if keycode < 256:
        if keycode == 0:
            keyname = "NUL"
        elif keycode < 27:
            keyname = "Ctrl-%s" % chr(ord('A') + keycode-1)
        else:
            keyname = "%s" % chr(keycode)
    else:
        keyname = "(%s)" % keycode
        
    return keyname