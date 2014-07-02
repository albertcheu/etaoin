#!/usr/bin/python

QUOTE = "'"
PIPE = "|"

#Makes the first n sentences from generativeGram.cfg
def gen(gramDict, n):

    pass

def pruneColor(gramDict, bgc, shapeDescList):
    #Get rid of colors that are not there
    colors = gramDict['C']
    for color in colors:
        inList = False
        for shapeDesc in shapeDescList:
            if shapeDesc[C] == color:
                inList = True
                break
            pass
        if bgc != color and not inList: gramDict['C'].remove(color)
        pass
    pass

def prunePoly(gramDict, shapeDescList):
    #Get rid of polygon types (triangle,quad,pent...)
    specifics = gramDict['SPECIFICS']
    for polyType in specifics:
        inList = False
        for shapeDesc in shapeDescList:
            if REVDEFNS[polyType] == shapeDesc[N]:
                inList = True
                break
            pass
        if not inList: gramDict['SPECIFICS'].remove(polyType)
        pass
    pass

def pruneGlobal(gramDict, shapeDescList):
    #Get rid of global locations
    globalLocs = ['center','top','top left','top right','left','right','bottom','bottom left','bottom right']
    for globalLoc in globalLocs:
        inList = False
        for shapeDesc in shapeDescList:
            if sameDesc(globalLoc.split(),shapeDesc[POLY].whereAmI()):
                inList = True
                break
            pass
        if not inList:
            if ' ' in globalLoc: pass
            elif globalLoc in gramDict['HORIZ']:
                gramDict['HORIZ'].remove(globalLoc)
                pass
            elif globalLoc in gramDict['VERT']:
                gramDict['VERT'].remove(globalLoc)
                pass
            else: gramDict['GLOBALLOC'].remove(globalLoc)
        pass
    pass

def pruneAdj(gramDict, shapeDescList):
    #Get rid of adjacencies
    haveAdj = False
    for i in range(len(shapeDescList)):
        for j in range(i, len(shapeDescList)):
            if adj(shapeDescList[i],shapeDescList[j]):
                haveAdj = True
                break
            pass
        if haveAdj: break
        pass
    if not haveAdj:
        gramDict.remove('ADJASSN')
        gramDict['PPS'].pop()
        pass
    pass

def prune(gramDict, bgc, shapeDescList):
    pruneColor(gramDict, bgc, shapeDescList)
    prunePoly(gramDict, shapeDescList)
    pruneGlobal(gramDict, shapeDescList)
    pruneAdj(gramDict, shapeDescList)
    pass

if __name__ == "__main__":
    f = open("generativeGram.cfg")
    lines = f.readlines()
    f.close()
    gramDict = {}
    for line in lines:
        tokens = line.strip().split()
        if len(tokens):
            production = tokens[0]
            children = []
            c = []
            for token in tokens[2:]:
                if token == PIPE:
                    children.append(c)
                    c = []
                    pass
                else: c.append(token.strip(QUOTE))
                pass
            if len(children) == 0: children.append(c)
            gramDict[production] = children
            pass
        pass
    print gramDict
    pass
