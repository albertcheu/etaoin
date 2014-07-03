QUOTE = "'"
PIPE = "|"

from copy import copy
from constants import N,C,POLY,REVDEFNS
from utility import adj
from Queue import Queue

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

def buildDAG(gramDict, combos, heights):
    def foo(s, h, combos, q):
        haveProd = False
        if s.isupper():
            haveProd = True
            if s not in combos:
                combos[s] = []
                q.put((s,h+1))
                pass
            pass
        return haveProd

    #BFS to find the height of each node/production
    q = Queue()
    q.put(('S', 0))
    while not q.empty():
        production, h = q.get()
        rule = gramDict[production]

        #Does this production refer to other productions?
        haveProd = False
        for item in rule:
            if type(item) == list:
                for token in item: haveProd |= foo(token, h, combos, q)
                pass
            elif item.isupper():
                foo(item, h, combos, q)
                haveProd = True
                pass
            pass
       
        if h not in heights: heights[h] = []
        heights[h].append(production)

        #all terminals
        if not haveProd: combos[production] = gramDict[production]

        pass
    pass

def stitchPossibilities(item, combos):
    #The item is a list of strings, each either a production or a terminal
    #This function finds all possible combinations of the sequence it describes
    #Each production has possibilites, stored in combos[prod...]
    def stitchRec(left, rightList):
        if len(rightList) == 0:
            if type(left) == str: return [left]
            return left
        rightList = stitchRec(rightList[0], rightList[1:])
        ans = []
        if type(left) == str:
            for entry in rightList: ans.append(left + ' ' + entry)
            pass
        else:
            for a in left:
                for b in rightList: ans.append(a + ' ' + b)
                pass
            pass
        return ans

    l = list((combos[x] if x.isupper() else x) for x in item)
    return stitchRec(l[0], l[1:])

#Makes the first n sentences from generativeGram.cfg
def gen(gramDict, n):
    print gramDict
    #Map each production to all the possible expansions of terminals
    combos,heights = {},{}
    combos['S'] = []
    
    buildDAG(gramDict, combos, heights)

    print combos
    print heights

    for i in range(len(heights)-1,-1,-1):
        print i
        for production in heights[i]:
            print production
            #Fill in combos[production]; guaranteed to have child productions!
            for item in gramDict[production]:
                if type(item) == list:
                    #combos[production] += stitchPossibilities(item, combos)
                    pass
                elif item.isupper(): combos[production] += combos[item]
                else: combos[production].append(item)
                pass
            if len(combos[production]) == 0: print 'oops', production
            pass

        pass
    return combos

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

