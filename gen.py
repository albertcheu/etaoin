QUOTE = "'"
PIPE = "|"

from copy import copy
from constants import N,C,POLY,REVDEFNS
from utility import adj
from Queue import Queue
#Makes the first n sentences from generativeGram.cfg
def gen(gramDict, n):
    q = Queue()
    stack = []
    #Map each production to all the possible expansions of terminals
    combos = {}
    q.put('S')
    while not q.empty():
        production = q.get()
        rules = gramDict[production]
        #find all unexpanded productions
        unexpanded = False
        haveProd = False
        for item in rules:
            if type(item) == list:
                for token in item:
                    if token.isupper():
                        haveProd = True
                        if token not in combos:
                            combos[token] = []
                            unexpanded = True
                            q.put(token)
                            pass
                        pass
                    pass
                pass
            elif item.isupper():
                haveProd = True
                if item not in combos:
                    combos[item] = []
                    unexpanded = True
                    q.put(item)
                    pass
                pass
            pass

        #put this on the stack for later
        if unexpanded: stack.append(production)
        #all terminals
        elif not haveProd: combos[production] = gramDict[production]
        #All productions have been expanded
        #else: stack.append(production)

        pass
    print combos
    print stack
    while len(stack) > 0:
        production = stack.pop()
        pass
    return

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
    #GramDict maps productions (i.e. S, ASSERTION, NP, etc.) to rules
    #a rule is a list of stuff, which we shall call items
    #each item in a rule is one possible way of expanding the production
    #if an item is a list, it denotes a sequence of terminals and/or more rules
    #if an item is a lowercase string, it denotes a terminal
    #if an item is an uppercase string, it denotes a nonterminal: a production
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
