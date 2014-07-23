#!/usr/bin/python
import wx

from random import seed, randint
seed()
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
        self.cpnl = wx.Panel(self,size=(110,160))

        (r,g,b) = (randint(0,255),randint(0,255),randint(0,255))
        self.rslider = wx.Slider(self, value=r, minValue=0,maxValue=255, size=(110,-1), style=wx.SL_HORIZONTAL)
        self.rslider.Bind(wx.EVT_SCROLL, self.OnSlider)

        self.gslider = wx.Slider(self, value=g, minValue=0,maxValue=255, size=(110,-1), style=wx.SL_HORIZONTAL)
        self.gslider.Bind(wx.EVT_SCROLL, self.OnSlider)

        self.bslider = wx.Slider(self, value=b, minValue=0,maxValue=255, size=(110,-1), style=wx.SL_HORIZONTAL)
        self.bslider.Bind(wx.EVT_SCROLL, self.OnSlider)

        self.cpnl.SetBackgroundColour(wx.Colour(r,g,b))

        self.nxt = wx.Button(self, label="Next")
        self.save = wx.Button(self, label="Save")

        self.nxt.Bind(wx.EVT_BUTTON,self.OnNext)
        self.save.Bind(wx.EVT_BUTTON,self.OnSave)

        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(self.cpnl)
        vbox.Add(self.rslider)
        vbox.Add(self.gslider)
        vbox.Add(self.bslider)
        vbox.Add(self.nxt)
        vbox.Add(self.save)
        return vbox

    def OnSlider(self, e):
        r = self.rslider.GetValue()
        g = self.gslider.GetValue()
        b = self.bslider.GetValue()
        self.cpnl.SetBackgroundColour(wx.Colour(r,g,b))
        pass

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
