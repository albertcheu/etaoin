#!/usr/bin/python
from os import listdir

import wx

from imageAnalysis import processImage
from interface import interface2

class ChatWindow(wx.Frame):
    def __init__(self, *args, **kwargs):
        super(ChatWindow,self).__init__(*args,**kwargs)
        self.Bind(wx.EVT_CLOSE, self.onClose)
        pass
    def onClose(self,eventThingy): exit(0)
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

class SelectionWindow(wx.Frame):
    def __init__(self, *args, **kwargs):
        super(SelectionWindow,self).__init__(*args,**kwargs)
        self.Bind(wx.EVT_CLOSE, self.onClose)
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)
        txt = wx.StaticText(panel,label='Please select the image to chat about')
        vbox.Add(txt)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        choices = []
        for i in range(12):
            if i < 6: choices.append('good%d'%(i+1))
            else: choices.append('bad%d'%(i-5))
            pass
        self.cbox = wx.ComboBox(panel, value='Image within set',
                                choices=choices, style=wx.CB_READONLY)
        hbox.Add(self.cbox, flag=wx.ALIGN_LEFT|wx.EXPAND)
        self.submit = wx.Button(panel,label='Submit')
        self.submit.Bind(wx.EVT_BUTTON,self.moveToChat)
        hbox.Add(self.submit,flag=wx.ALIGN_RIGHT)
        vbox.Add(hbox,flag=wx.TOP,border=10)

        panel.SetSizer(vbox)
        self.Centre()
        self.Show()
        pass
    def onClose(self,eventThingy): exit(0)
    def setPS(self, ps): self.ps = ps
    def moveToChat(self, eventThingy):
        if len(self.cbox.GetValue().split()) > 1: return
        picked = self.cbox.GetValue()
        fname = 'problemSets/%s/%s.png' % (self.ps,picked)
        #self.Close()
        styleSet = wx.MINIMIZE_BOX|wx.CLOSE_BOX|wx.CLIP_CHILDREN|wx.CAPTION
        cw = ChatWindow(None,size=(800,650),title='Chat Window',style=styleSet)
        cw.start(fname)
        pass
    pass

def startChat(ps):
    app = wx.App()
    styleSet = wx.MINIMIZE_BOX|wx.CLOSE_BOX|wx.CLIP_CHILDREN|wx.CAPTION
    sw = SelectionWindow(None,size=(280,90),
                         title='Selection Window',style=styleSet)
    sw.setPS('ps%d'%ps)    
    app.MainLoop()
