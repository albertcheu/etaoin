QUOTE = "'"
PIPE = "|"

from copy import copy
from constants import N,C,POLY,REVDEFNS
from utility import adj
#Makes the first n sentences from generativeGram.cfg
def gen(gramDict, n):
    def combo(leftList, rightList):
        ans = []
        if len(rightList) == 1:
            for item in rightList: ans.append([item])
            pass
        else:
            for item in leftList:
                for newList in combo(rightList[0],rightList[1:]):
                    ans.append([item]+newList)
                    pass
                pass
            pass
        return ans

    def genRec(gramDict, sym):
        rules = gramDict[sym]
        print rules
        #One rule
        if len(rules)==1 and type(rules[0])==str: rules = [rules]
        ans = []
        for rule in rules:
            slots = []
            if type(rule)==str:
                if rule.isupper(): slots.append(genRec(gramDict, rule))
                else: slots.append(rule)
                pass
            else:
                for token in rule:
                    if token.isupper(): slots.append(genRec(gramDict, token))
                    else: slots.append(token)
                    pass
                pass
            if len(slots) == 1: ans = combo([], slots)
            else: ans = combo(slots[0],slots[1:])
            pass
        return ans
    return genRec(gramDict, 'S')[:n]


def pruneColor(gramDict, bgc, shapeDescList):
    #Get rid of colors that are not there
    colors = copy(gramDict['C'])
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
    specifics = copy(gramDict['SPECIFICS'])
    for polyType in specifics:
        inList = False
        for shapeDesc in shapeDescList:
            if REVDEFNS[polyType] == shapeDesc[N]:
                inList = True
                break
            pass
        if not inList:
            gramDict['SPECIFICS'].remove(polyType)
            gramDict['SPECIFICP'].remove(polyType+'s')
            pass
        pass
    pass

def pruneGlobal(gramDict, shapeDescList):
    #Get rid of global locations
    globalLocs = ['center','top','top left','top right','left','right','bottom','bottom left','bottom right']
    for globalLoc in globalLocs:
        inList = False
        for shapeDesc in shapeDescList:
            if shapeDesc[POLY].sameDesc(globalLoc.split()):
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
        gramDict['ASSERTION'].remove('ADJASSN')
        gramDict['PPS'].pop()
        pass
    pass

def prune(gramDict, bgc, shapeDescList):
    pruneColor(gramDict, bgc, shapeDescList)
    prunePoly(gramDict, shapeDescList)
    pruneGlobal(gramDict, shapeDescList)
    pruneAdj(gramDict, shapeDescList)
    pass

def getGramDict():
    f = open("generativeGram.cfg")
    lines = f.readlines()
    f.close()
    gramDict = {}
    for line in lines:
        if len(line) > 2:
            p = tuple(t.strip() for t in line.strip().split('->'))
            production,rhs = p
            tokens = tuple(t.strip() for t in rhs.strip().split('|'))
            children = []
            for token in tokens:
                c = list(t.strip(QUOTE) for t in token.strip().split())
                if len(c) == 1: c = c[0]
                children.append(c)
                pass
            gramDict[production] = children
            pass
        pass
    return gramDict
