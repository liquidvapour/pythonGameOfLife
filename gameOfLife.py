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

import diagnostics
from diagnostics import timeMe

rPentomino = [(1,2),(2,1),(2,2),(2,3),(3,1)]
acorn = [(1,3),(2,1),(2,3),(4,2),(5,3),(6,3),(7,3)]
dieHard = [(1,2),(2,2),(2,3),(7,1),(6,3),(7,3),(8,3)]

info = {}

def neighboursGenerator():
    for i in range(-1, 2):
        for j in range(-1, 2):
            if not (i == 0 and j == 0):
                yield (i,j)

neighbours = list(neighboursGenerator())

@timeMe
def findDeadCellsNeighbours(currentGen):
    result = {}
    cellsConsidered = 0
    for testCell in [(x + i, y + j) for x, y in currentGen for i, j in neighbours]:
        if testCell not in currentGen:
            if not result.has_key(testCell):
                result[testCell] = 1
            else:
                result[testCell] += 1
            cellsConsidered += 1
    info["dead cells considered"] = cellsConsidered
    return result

def findNewCells(currentGen):
    deadCellsNeighbours = findDeadCellsNeighbours(currentGen).items()
    return [x[0] for x in deadCellsNeighbours if x[1] == 3]

def isNeighbour(currentCell, other):
    return other != currentCell and \
           other[0] >= currentCell[0] - 1 and other[0] <= currentCell[0] + 1 and \
           other[1] >= currentCell[1] - 1 and other[1] <= currentCell[1] + 1


def getNeighbours(currentCell, currentGen):    
    return [x for x in currentGen if isNeighbour(currentCell, x)]

@timeMe
def getCellsThatLiveOn(currentGen):
    nextGen = []
    for cell in currentGen:
        neigbours = len(getNeighbours(cell, currentGen))
        if neigbours == 2 or neigbours == 3:
            nextGen.append(cell)
    return nextGen

@timeMe
def calcGen(currentGen):
    """rules:
 Any live cell with fewer than two live neighbours dies,
   as if caused by under-population.
 Any live cell with two or three live neighbours lives on to the next generation.
 Any live cell with more than three live neighbours dies,
   as if by overcrowding.
 Any dead cell with exactly three live neighbours becomes a live cell,
   as if by reproduction."""
    nextGen = set(getCellsThatLiveOn(currentGen))
    
    nextGen = nextGen.union(findNewCells(currentGen))

    info["cells in gen"] = len(nextGen)
    return list(nextGen)
