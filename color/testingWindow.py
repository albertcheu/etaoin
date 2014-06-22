#!/usr/bin/python
import wx

import random
random.seed()
from pickle import load

from treeMaker import belong
from constants import COLORS

def randColor():
    r = random.randint(0,255)
    g = random.randint(0,255)
    b = random.randint(0,255)
    return wx.Colour(r,g,b)

class TestFrame(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title, style=wx.CLOSE_BOX|wx.CAPTION, size=(200,370))

        hbox = wx.BoxSizer(wx.HORIZONTAL)

        #Left side of window
        hbox.Add(self.makeLeftHalf())

        #Right side of window
        hbox.Add(self.makeRightHalf())

        self.SetSizer(hbox)
        self.Centre()
        self.Show(True)

        trees = load(open("decisionTrees.pkl","rb"))
        self.decisionTrees = {}
        for col in COLORS: self.decisionTrees[col] = belong(trees[col])

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

        self.nxt.Bind(wx.EVT_BUTTON,self.OnNext)

        vbox = wx.BoxSizer(wx.VERTICAL)
        self.cpnl.SetBackgroundColour(randColor())
        vbox.Add(self.cpnl)
        vbox.Add(self.nxt)

        return vbox

    def OnNext(self, e):
        #Clicked the Next button

        #Change RGB values to another random triplet
        self.cpnl.SetBackgroundColour(randColor())
        #Get RGB values
        col = self.cpnl.GetBackgroundColour()
        (r,g,b) = (col.Red(),col.Green(),col.Blue())

        #Show which color flags the tree believes are applicable
        for i in range(len(COLORS)):
            cb = self.checkBoxes[i]
            col = COLORS[i]
            cb.SetValue(self.decisionTrees[col](r,g,b))
            pass

        pass

if __name__ == "__main__":
    app = wx.App(False)
    frame = TestFrame(None, "Testing Window")
    app.MainLoop()
    pass
