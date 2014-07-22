#!/usr/bin/python
import wx

from random import seed, randint
seed()
from pickle import load

from constants import COLORS
from treeMaker import belong

def randColor():
    r = random.randint(0,255)
    g = random.randint(0,255)
    b = random.randint(0,255)
    return wx.Colour(r,g,b)

class TestFrame(wx.Frame):
    def __init__(self, parent, title):
        self.data = []

        wx.Frame.__init__(self, parent, title=title, style=wx.CLOSE_BOX|wx.CAPTION, size=(200,370))

        hbox = wx.BoxSizer(wx.HORIZONTAL)

        #Left side of window
        hbox.Add(self.makeLeftHalf())

        #Right side of window
        hbox.Add(self.makeRightHalf())

        trees = load(open("decisionTrees.pkl","rb"))
        self.decisionTrees = {}
        for col in COLORS: self.decisionTrees[col] = belong(trees[col])

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
        
        self.texts, self.sliders = [], []
        for i in range(3):
            val = randint(0,255)
            self.texts.append(wx.StaticText(self, label=str(val),
                                            style=wx.ALIGN_LEFT))
            self.sliders.append(wx.Slider(self, value=val, minValue=0,
                                          maxValue=255,size=(110,-1),
                                          style=wx.SL_HORIZONTAL))
            self.sliders[-1].Bind(wx.EVT_SCROLL, self.OnSlider)
            pass
        (r,g,b) = (s.GetValue() for s in self.sliders)
        self.cpnl.SetBackgroundColour(wx.Colour(r,g,b))

        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(self.cpnl)
        for i in range(3): vbox.AddMany((self.texts[i],self.sliders[i]))
        
        return vbox

    def OnSlider(self, e):
        (r,g,b) = (s.GetValue() for s in self.sliders)
        self.cpnl.SetBackgroundColour(wx.Colour(r,g,b))
        color = (r,g,b)
        for i in range(3): self.texts[i].SetLabel(str(color[i]))

        #Show which color flags the tree believes are applicable
        for i in range(len(COLORS)):
            cb = self.checkBoxes[i]
            col = COLORS[i]
            cb.SetValue(self.decisionTrees[col](r,g,b))
            pass
        pass

    pass

if __name__ == "__main__":
    app = wx.App(False)
    frame = TestFrame(None, "Testing Window")
    app.MainLoop()
    pass
