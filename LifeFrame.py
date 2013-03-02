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

import sys
import traceback

import wx
from wx.lib.wordwrap import wordwrap
import gameOfLife
import wxHelper
import diagnostics
from diagnostics import timeMe

import multiprocessing
from multiprocessing import Process, Pipe

def UpdateThreaded(conn, firstGen):
    stop = False
    nextGen = firstGen
    while not stop:        
        nextGen = gameOfLife.calcGen(nextGen)
        conn.send(nextGen)
        if conn.poll():
            stop = conn.recv() == "stop"
            

class LifeFrame(wx.Frame):
    def __init__(self, parent, ID, title, pos=wx.DefaultPosition,
                 size=wx.DefaultSize,
                 style=wx.DEFAULT_FRAME_STYLE,
                 gen=gameOfLife.rPentomino):
        wx.Frame.__init__(self, parent, ID, title, pos, size, style)
        self._gen = gen
        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)

        self.Bind(wx.EVT_MOTION, self.OnMotion)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_TIMER, self.OnTimer)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.Bind(wx.EVT_KEY_UP, self.OnKeyUp)

        self._offset = (-20,-20)
        self._mouseMoving = False
        self._lastGenTime = 0.0
        self._background = wx.Brush(wx.WHITE, wx.SOLID)        
        self._background = wx.Brush(wx.Color(63,63,63))
        self._cellColor = wx.Color(183,135,135)
        self._cellBrush = wx.Brush(self._cellColor)
        self._cellPen = wx.Pen(self._cellColor)
        self._textColor = wx.Color(223,223,191)

        self._timer = wx.Timer(self)
        self._timer.Start(1000/16)      

        self._generations = 0
        self._minX = 0
        self._minY = 0
        self._maxX = 0
        self._maxY = 0
        self._info = {}

        self._set_up_multiprocessing()
        
    def _set_up_multiprocessing(self):
        print "CPUs: {0}.".format(multiprocessing.cpu_count())
    
        self._parent_conn, child_conn = Pipe()
        self._process = Process(target=UpdateThreaded, args=(child_conn, self._gen))
        self._process.start()

    
    def OnKeyUp(self, event):        
        key = wxHelper.GetKeyName(event.GetKeyCode())
        print "key up: {0}".format(key)
        if key == "H":
            self._show_about()
        
    def OnMotion(self, event):        
        if event.LeftIsDown():
            if self._mouseMoving:
                lastX, lastY = self._lastPosition
                x, y = event.GetPosition()
                movementX, movementY = (lastX - x, lastY - y)
                offsetX, offsetY = self._offset                
                self._offset = ((offsetX + movementX/10.0), (offsetY + movementY/10.0))
                self._lastPosition = (x, y)
            else:                
                self._mouseMoving = True
                self._lastPosition = event.GetPosition()
        else:
            self._mouseMoving = False

    def OnClose(self, event):
        print "stopping timer"
        self._timer.Stop()
        print "sending stop to background process."
        self._parent_conn.send("stop")        
        self._empty_connection(self._parent_conn)
        print "joining background process."        
        self._process.join()        
        print "process is alive: {0}".format(self._process.is_alive())        
        print "destroying self."
        self.Destroy()

    def _empty_connection(self, conn):
        print "clearing connection."
        itemsCleared = 0
        while conn.poll():
            buffer = conn.recv()
            itemsCleared += 1
        print "connection cleared of {0} items.".format(itemsCleared)
        
    @timeMe
    def OnPaint(self, event):
        try:
            dc = wx.BufferedPaintDC(self)
            dc.BeginDrawing()
            dc.SetBackground(self._background)
            dc.Clear()
            dc.SetBrush(self._cellBrush)
            dc.SetPen(self._cellPen)
            self.RenderGen(self._gen, dc)
            
            self.RenderSizeBars(self._gen, dc)
            
            dc.SetTextForeground(self._textColor)
            lastCell = self.RenderInfo(dc, self._info)
            lastCell = self.RenderInfo(dc, gameOfLife.info, lastCell)
            self.RenderInfo(dc, diagnostics.perfInfo, lastCell)
            dc.EndDrawing()
            if (len(self._gen) == 0): self._timer.Stop()
        except Exception:
            self._timer.Stop()
            exc_type, exc_value, exc_traceback = sys.exc_info()
            print "*** OnPaint exception:"
            traceback.print_exception(exc_type, exc_value, exc_traceback)
    
    def OnTimer(self, event):
        self.Update()
        self.Refresh()

    @timeMe
    def Update(self):
        if self._parent_conn.poll():            
            self._gen = self._parent_conn.recv()
            self._generations += 1
            self._info["generations"] = self._generations
            
    @timeMe
    def RenderGen(self, gen, dc):        
        width, height = self.GetClientSize()
        screenWidthInCells = width / 10
        screenHeightInCells = height / 10
        offsetX = round(self._offset[0])
        offsetY = round(self._offset[1])
        for x, y in gen:
            if (x >= offsetX and y >= offsetY and 
                x < offsetX + screenWidthInCells and y < offsetY + screenHeightInCells):
                self.DrawCel((x - offsetX, y - offsetY), dc)

    @timeMe
    def GetBounds(self, gen):
        if len(gen) > 0:
            minX = min([i[0] for i in gen])
            maxX = max([i[0] for i in gen])
            minY = min([i[1] for i in gen])
            maxY = max([i[1] for i in gen])
        else:
            minX = 0
            maxX = 0
            minY = 0
            maxY = 0
            
        boardWidth = maxX - minX
        boardHeight = maxY - minY

        return (minX, minY, boardWidth, boardHeight)

    @timeMe
    def RenderSizeBars(self, gen, dc):
        width, height = self.GetClientSize()
        screenWidthInCells = width / 10
        screenHeightInCells = height / 10
        
        minX, minY, boardWidth, boardHeight = self.GetBounds(gen)

        factorOfBoardShowX = (1.0 - (boardWidth - screenWidthInCells) / float(boardWidth)) if boardWidth > screenWidthInCells else 1.0
        factorOfBoardShowY = (1.0 - (boardHeight - screenHeightInCells) / float(boardHeight)) if boardHeight > screenHeightInCells else 1.0

        horizontalPixelsPerBoardCell = width / boardWidth if boardWidth > 0 else 0
        verticalPixelsPerBoardCell = width / boardHeight if boardHeight > 0 else 0

        horizontalOffSet = self._offset[0] - minX# if minX < self._offset[0] else 0
        if horizontalOffSet > boardWidth - screenWidthInCells:
            horizontalOffSet = boardWidth - screenWidthInCells
        elif horizontalOffSet < 0:
            horizontalOffSet = 0

        verticalOffset = self._offset[1] - minY if minY < self._offset[1] else 0

        dc.DrawRectangle(horizontalOffSet * horizontalPixelsPerBoardCell, height - 4, screenWidthInCells * horizontalPixelsPerBoardCell, 4)
        dc.DrawRectangle(width - 4, verticalOffset * verticalPixelsPerBoardCell, 4, screenHeightInCells * verticalPixelsPerBoardCell)

        
        
    @timeMe
    def RenderInfo(self, dc, info, startAt = 0):
        i = startAt
        for name in sorted(info, key=str.lower):
            dc.DrawTextPoint("{0}: {1}".format(name, info[name]), (0,i))
            i += 20
        return i

    @timeMe
    def DrawCel(self, cell, dc):
        dc.DrawRectangle(cell[0] * 10, cell[1] * 10, 10, 10)
        
    def _show_about(self):
        info = wx.AboutDialogInfo()
        info.Name = "pythonGameOfLife"
        info.Version = "0.0.1"
        info.Copyright = "(C) 2013 Ra-el Peters"
        info.Description = wordwrap(
            "Simple Python implementation of Conway's Game of Life.",
            350, wx.ClientDC(self))
        info.WebSite = ("https://github.com/liquidvapour/pythonGameOfLife", "pythonGameOfLife GitHub page")
        info.Developers = [ "Ra-el Peters" ]

        licenceFile = open("SIMPLE LICENCE.txt", "r")
        
        info.License = wordwrap(licenceFile.read(), 500, wx.ClientDC(self))

        wx.AboutBox(info)

def main(startGen = gameOfLife.acorn):

    print "pythonGameOfLife  Copyright (C) 2013  Ra-el Peters"
    print "This program comes with ABSOLUTELY NO WARRANTY; for details type 'h'."
    print "This is free software, and you are welcome to redistribute it"
    print "under certain conditions; type 'h' for details."

    app = wx.PySimpleApp()
    
    d = LifeFrame(None, -1, "Test",gen=startGen)
    d.Show()
    app.MainLoop()

if __name__ == "__main__":
    main()
