#!/usr/bin/python
import wx

import random
random.seed()

from pickle import dump
from time import localtime
from constants import COLORS

def randColor():
    r = random.randint(0,255)
    g = random.randint(0,255)
    b = random.randint(0,255)
    return wx.Colour(r,g,b)

def to2digit(num):
    ans = str(num)
    if len(ans) < 2: ans = "0"+ans
    return ans

def makeTime():
    t = localtime()
    #MMDDHHMinMin
    month = to2digit(t.tm_mon)
    day = to2digit(t.tm_mday)
    hour = to2digit(t.tm_hour)
    mn = to2digit(t.tm_min)
    return month+day+hour+mn

class TrainFrame(wx.Frame):
    def __init__(self, parent, title):
        self.data = []

        wx.Frame.__init__(self, parent, title=title, style=wx.CLOSE_BOX|wx.CAPTION, size=(200,370))

        hbox = wx.BoxSizer(wx.HORIZONTAL)

        #Left side of window
        hbox.Add(self.makeLeftHalf())

        #Right side of window
        hbox.Add(self.makeRightHalf())

        self.SetSizer(hbox)
        self.Centre()
        self.Show(True)

        pass

    def makeLeftHalf(self):
        self.checkBoxes = []
        vbox = wx.BoxSizer(wx.VERTICAL)
        for i in range(len(COLORS)):
            cb = wx.CheckBox(self, label=COLORS[i].title())
            self.checkBoxes.append(cb)
            vbox.Add(cb, flag=wx.TOP|wx.BOTTOM, border=2)            
            pass
        return vbox
    def makeRightHalf(self):
        self.cpnl = wx.Panel(self,size=(110,240))
        self.nxt = wx.Button(self, label="Next")
        self.save = wx.Button(self, label="Save")

        self.nxt.Bind(wx.EVT_BUTTON,self.OnNext)
        self.save.Bind(wx.EVT_BUTTON,self.OnSave)

        vbox = wx.BoxSizer(wx.VERTICAL)
        self.cpnl.SetBackgroundColour(randColor())
        vbox.Add(self.cpnl)
        vbox.Add(self.nxt)
        vbox.Add(self.save)
        return vbox

    def OnNext(self, e):
        #Clicked the Next button

        #Determine the flags selected (what colors)
        chosenColors = []
        for i in range(len(COLORS)):
            cb = self.checkBoxes[i]
            if cb.IsChecked():
                cb.SetValue(False)
                chosenColors.append(COLORS[i])
                pass
            pass
        
        #Get RGB values
        col = self.cpnl.GetBackgroundColour()
        (r,g,b) = (col.Red(),col.Green(),col.Blue())
        #Store pairing
        self.data.append((r,g,b,chosenColors))
        
        #Change RGB values to another random triplet
        self.cpnl.SetBackgroundColour(randColor())
        pass
    
    def OnSave(self, e):
        #Write data to a file
        fname = makeTime()
        dump(self.data, open("colorCorpus/"+fname,"wb"))
        #Clear data
        self.data = []
        pass

    pass

if __name__ == "__main__":
    app = wx.App(False)
    frame = TrainFrame(None, "Training Window")
    app.MainLoop()
    pass
