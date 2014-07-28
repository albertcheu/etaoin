#!/usr/bin/python
import wx

from imageAnalysis import processImage
from interface import interface2

class ChatWindow(wx.Frame):
    def __init__(self, *args, **kwargs):
        super(ChatWindow,self).__init__(*args,**kwargs)
        pass
    def start(self,fname):
        panel = wx.Panel(self)

        flags = wx.LEFT|wx.RIGHT|wx.TOP|wx.BOTTOM|wx.EXPAND

        hbox = wx.BoxSizer(wx.HORIZONTAL)

        png = wx.Image(fname,wx.BITMAP_TYPE_PNG)
        pngWidget = wx.StaticBitmap(panel,wx.ID_ANY,wx.BitmapFromImage(png))
        hbox.Add(pngWidget,flag=wx.CENTER)
        self.bgc,self.shapeDescList = processImage(fname)

        vbox = wx.BoxSizer(wx.VERTICAL)

        self.txt = wx.TextCtrl(panel,style=wx.TE_MULTILINE|wx.TE_READONLY)
        self.txt.SetValue('Hello')
        vbox.Add(self.txt,proportion=1,flag=flags,border=10)

        self.txtInput = wx.TextCtrl(panel,-1)
        vbox.Add(self.txtInput,flag=flags,border=10)

        self.submit = wx.Button(panel,label='Submit')
        self.submit.Bind(wx.EVT_BUTTON, self.askOrAssert)
        vbox.Add(self.submit,flag=flags, border=10)
        
        hbox.Add(vbox,flag=flags,proportion=1)

        panel.SetSizer(hbox)
        self.Centre()
        self.Show()
        pass
    def askOrAssert(self, eventThingy):
        oldvalue = self.txt.GetValue()
        userInput = str(self.txtInput.GetValue())
        response = interface2(self.bgc,self.shapeDescList,userInput)
        self.txt.SetValue(oldvalue+'\nYou: '+userInput+'\n'+response)
        self.txtInput.SetValue('')
        pass
    pass

if __name__ == '__main__':
    app = wx.App(0)
    styleSet = wx.MINIMIZE_BOX|wx.CLOSE_BOX|wx.CLIP_CHILDREN|wx.CAPTION
    cw = ChatWindow(None,size=(800,650),title='Chat Window',style=styleSet)
    fname = 'problemSets/ps1/bad3.png'
    cw.start(fname)
    app.MainLoop()
