#!/usr/bin/python
from random import choice
from os import listdir
from subprocess import call

import wx

from constants import COLORS, DEFNS
from analysis import analyzeProblemSet
from makeScene import makeScene1

sideOptions = map(str, sorted(DEFNS.keys()) )

def drawLines(panel,flagSet,vsizer):
    #Aesthetics
    vsizer.Add(wx.StaticLine(panel), flag=wx.EXPAND|flagSet, border=5)
    vsizer.Add(wx.StaticLine(panel), flag=wx.EXPAND|flagSet, border=2)
    pass

class SceneInput(wx.Frame):
    def __init__(self, *args, **kwargs):
        super(SceneInput, self).__init__(*args, **kwargs)
        panel = wx.Panel(self)
        flagSet = wx.LEFT|wx.TOP
        
        vsizer = wx.BoxSizer(wx.VERTICAL)
        vsizer.Add(self.makeTop(panel, flagSet),flag=wx.ALIGN_CENTER)
        drawLines(panel, flagSet, vsizer)

        vsizer.Add(self.makeGrid(panel), flag=flagSet,border=10)
        drawLines(panel, flagSet, vsizer)

        self.submit = wx.Button(panel,label='Submit!')
        self.submit.Bind(wx.EVT_BUTTON, self.submitForm)
        vsizer.Add(self.submit,flag=wx.ALIGN_CENTER|wx.TOP, border=5)
        panel.SetSizer(vsizer)

        self.Centre()
        self.Show()
        pass

    def makeTop(self, panel, flagSet):
        bgcText = wx.StaticText(panel,label='Background Color:')
        self.bgcSelect = wx.ComboBox(panel,choices=COLORS, style=wx.CB_READONLY)
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        hsizer.Add(bgcText, flag=flagSet, border = 10)
        hsizer.Add(self.bgcSelect,flag=flagSet, border = 5)    
        return hsizer

    def makeGrid(self, panel):
        gs = wx.GridSizer(3,3,5,5)
        regions = ('Top-left','Top','Top-right','Left','Center',
                   'Right','Bottom-left','Bottom','Bottom-right')
        self.colorList, self.sideList = [],[]
        for r in regions:
            regionLabel = wx.StaticText(panel,label=r,style=wx.ALIGN_CENTRE)
            colorChoice = wx.ComboBox(panel,value='Select color',choices=COLORS,style=wx.CB_READONLY)
            self.colorList.append(colorChoice)
            sideChoice = wx.ComboBox(panel,value='Select no. sides',choices=sideOptions,style=wx.CB_READONLY)
            self.sideList.append(sideChoice)

            vsizer2 = wx.BoxSizer(wx.VERTICAL)
            vsizer2.AddMany((regionLabel,colorChoice,sideChoice))
            gs.Add(vsizer2)
            pass
        return gs

    def saveLabel(self, label): self.label = label

    def submitForm(self, eventThing):
        bgc = str(self.bgcSelect.GetValue())
        shapeDescList = []
        for i in range(9):
            #uc = unicode color
            uc,n = self.colorList[i].GetValue(),self.sideList[i].GetValue()
            if uc in COLORS and n in sideOptions:
                shapeDescList.append((str(uc), n, i))
                pass
            pass
        if bgc in COLORS and len(shapeDescList) > 0:
            f = open(self.label,'w')
            f.write(bgc+'\n'+str(len(shapeDescList))+'\n')
            for (c,n,i) in shapeDescList: f.write(c+'\n'+n+'\n'+str(i)+'\n')
            f.close()
            self.Close(True)
            pass
        pass

    pass

def creationGUI(label):
    #label = good1..6, bad1..6
    app = wx.App()
    styleSet = wx.MINIMIZE_BOX|wx.CLOSE_BOX|wx.CLIP_CHILDREN|wx.CAPTION
    si = SceneInput(None, size=(600,350), title=label, style=styleSet)
    si.saveLabel(label)
    app.MainLoop()
    pass

class Start(wx.Frame):
    def __init__(self, *args, **kwargs):
        super(Start, self).__init__(*args, **kwargs)
        panel = wx.Panel(self)
        txt = '''
Hello! This is Etaoin (or Etta Owen).

This system finds sentences that are
true for 6 images, false for another 6.
The images are of simple polygons.
You can make new problem sets!

Please choose one of the choices.

The selection of problem set is
irrelevant to 'make' but required
when deleting or analyzing.
'''

        self.txt = wx.StaticText(panel,label=txt)
        self.make = wx.RadioButton(panel,label='Make a problem set',
                                   style=wx.RB_GROUP)
        self.delete = wx.RadioButton(panel,label='Delete a problem set')
        self.analyze = wx.RadioButton(panel,label='Analyze a problem set')
        self.fnames = wx.ComboBox(panel,choices=listdir('problemSets/'),
                                  style=wx.CB_READONLY,value='Problem set...')
        self.select = wx.Button(panel, label='Next')
        self.select.Bind(wx.EVT_BUTTON, self.nxt)

        szr = wx.BoxSizer(wx.VERTICAL)
        szr.AddMany((self.txt,self.make,self.delete, self.analyze,self.fnames))
        szr.Add(self.select,flag=wx.ALIGN_RIGHT|wx.TOP|wx.RIGHT,border=10)
        panel.SetSizer(szr)

        self.Centre()
        self.Show()
        pass
    def nxt(self, eventThingy):
        fnames = listdir('problemSets/')
        fname = self.fnames.GetValue()

        if self.delete.GetValue(): f,word = deleteProblemSet,'delete'
        elif self.analyze.GetValue(): f,word = analyzeProblemSet,'analyze'
        #Make a problem set
        if self.make.GetValue():
            lastProblemSet = fnames[-1][-1] if len(fnames) else '0'            
            ps = int(lastProblemSet)+1
            self.Close()
            createProblemSet(ps)
            exit(0)
            pass
        #Delete or analyze
        if fname in fnames:
            ps = int(fname[-1])
            self.Close()
            message = f(ps)
            wx.MessageBox(message,'Alert!',wx.OK)
            exit(0)
            pass
        else: print 'Please select a problem set to',word

        pass
    pass

def startGUI():
    #What the user sees first
    #Choose between making new problem set, deleting old one, or analyzing
    app = wx.App()
    styleSet = wx.MINIMIZE_BOX|wx.CLOSE_BOX|wx.CLIP_CHILDREN|wx.CAPTION
    Start(None,size=(250,400),title='Etaoin, or Etta Owen',style=styleSet)
    app.MainLoop()
    pass

def deleteProblemSet(ps):
    #rm -r that directory
    call(['rm', '-r', 'problemSets/ps%d/'%ps])

    #rename subsequent directories, if any
    ps += 1
    dirname = 'ps%d'%ps
    while dirname in listdir('problemSets'):
        call(['mv', 'problemSets'+dirname, 'problemSets/ps%d'%(ps-1)])
        ps += 1
        dirname = 'ps%d'%ps
        pass
    return 'Deleted problem set %d.\nNote that subsequent problem sets have been renamed as well (if you delete ps3, ps4 is renamed ps3)'%ps

def createProblemSet(ps):
    call(['mkdir', 'problemSets/ps%d'%ps])
    for i in range(1,7):
        fname = 'problemSets/ps%d/good%d'%(ps,i)
        creationGUI(fname)
        makeScene1(fname)
        pass
    for i in range(1,7):
        fname = 'problemSets/ps%d/bad%d'%(ps,i)
        creationGUI(fname)
        makeScene1(fname)
        pass
    files = listdir('problemSets/ps%d'%ps)
    if len(files) < 12:
        print 'Oh, you skipped one'
        call(['rm', '-r', 'problemSets/ps%d'%ps])
        pass
    call(['gnome-open', 'problemSets/ps%d/good1.png'%ps])
    pass

if __name__ == '__main__':
    startGUI()
    pass
