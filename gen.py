QUOTE = "'"
PIPE = "|"

from copy import copy
from constants import N,C,POLY,REVDEFNS, COLORS,NUMS,SNUM
from utility import adj, left, right, above, below
from filters import filterByCN

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

def buildDAG(gramDict, combos, dag):
    def foo(s, gramDict, combos, dag):
        haveProd = False
        if s.isupper():
            haveProd = True
            if s not in combos: explore(s, gramDict, combos, dag)
            pass
        return haveProd

    def explore(production, gramDict, combos, dag):
        combos[production] = []
        rule = gramDict[production]

        #Does this production refer to other productions?
        haveProd = False
        for item in rule:
            if type(item) == list:
                for token in item:
                    haveProd |= foo(token, gramDict, combos, dag)
                    pass
                pass
            elif item.isupper():
                foo(item, gramDict, combos, dag)
                haveProd = True
                pass
            pass

        #all terminals
        if not haveProd: combos[production] = gramDict[production]
        else: dag.append(production)
        pass

    explore('S', gramDict, combos, dag)
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
            for entry in rightList:
                if not entry.endswith(left): ans.append(left + ' ' + entry)
                pass
            pass
        else:
            for a in left:
                for b in rightList:
                    if not b.endswith(a): ans.append(a + ' ' + b)
                    pass
                pass
            pass
        return ans

    l = list((combos[x] if x.isupper() else x) for x in item)
    return stitchRec(l[0], l[1:])

#Makes the first n sentences from generativeGram.cfg
def gen(gramDict, n, shapeDescList):
    #Map each production to all the possible expansions of terminals
    combos,dag = {},[]
    combos['S'] = []
    
    buildDAG(gramDict, combos, dag)
    print dag

    for production in dag[:19]:
        #Fill in combos[production]; guaranteed to have child productions!
        for item in gramDict[production]:
            if type(item) == list:
                combos[production] += stitchPossibilities(item, combos)
                pass
            elif item.isupper(): combos[production] += combos[item]
            else: combos[production].append(item)
            pass

        pruneCombos(production, combos, shapeDescList)
        print production, len(combos[production])
        pass
    
    return combos

def pruneCombos(production, combos, shapeDescList):
    #post-pruning: eliminate combos of color and nouns that DNE
    if production in ('NPSINGTERT','NPPLUR1SEC'):
        newList = []
        for item in combos[production]:
            if len(filterByCN(item.split(),shapeDescList)) > 0:
                newList.append(item)
                pass
            pass
        combos[production] = newList
        pass
    #eliminate combos of enumeration & nouns that DNE (i.e. five triangles)
    elif production in ('NPPLUR1','NPSINGSEC'):
        newList = []
        for item in combos[production]:
            
            itemList = item.split()
            cn = [itemList[-1]]
            if len(itemList) > 1 and itemList[-2] in COLORS:
                cn = [itemList[-2]] + cn
                pass
            notIn = 0
            for num in NUMS:
                if num in item:
                    good = SNUM[num] <= len(filterByCN(cn,shapeDescList))
                    if good: newList.append(item)            
                    pass
                else: notIn += 1
                pass
            if notIn == len(NUMS): newList.append(item)
            pass
        combos[production] = newList
        pass
    pass

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
            if globalLoc.split() in gramDict['CORNERLOC']:
                gramDict['CORNERLOC'].remove(globalLoc.split())
                pass
            elif globalLoc in gramDict['HORIZ']:
                gramDict['HORIZ'].remove(globalLoc)
                pass
            elif globalLoc in gramDict['VERT']:
                gramDict['VERT'].remove(globalLoc)
                pass
            else: gramDict['GLOBALLOC'].remove(globalLoc)
        pass
    for i in range(len(gramDict['CORNERLOC'])):
        gramDict['CORNERLOC'][i] = ' '. join(gramDict['CORNERLOC'][i])
        pass
    for loc in ('CORNERLOC','HORIZ','VERT'):
        if len(gramDict[loc]) == 0:
            gramDict.remove(loc)
            gramDict['GLOBALLOC'].remove(loc)
            pass
        pass
    if len(gramDict['GLOBALLOC'])==0: gramDict.remove('GLOBALLOC')
    pass

def pruneAdj(gramDict, shapeDescList):
    def pruneCardinal(gramDict, shapeDescList):
        for r in range(4):
            relRule = (left,right,above,below)[r]
            present = False
            for i in range(len(shapeDescList)):
                for j in range(i, len(shapeDescList)):
                    a,b = shapeDescList[i],shapeDescList[j]
                    if relRule(a,b) or (b,a):
                        present = True
                        break                    
                    pass
                if present: break
                pass
            if not present: del gramDict['CARDINAL'][r:r+1]
            pass
        pass
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
        gramDict.remove('P2')
        gramDict.remove('ADJACENT')
        gramDict.remove('CARDINAL')
        gramDict['ASSERTION'].pop()
        gramDict['PPS'].pop()
        pass
    else: pruneCardinal(gramDict, shapeDescList)
    pass

def prune(gramDict, bgc, shapeDescList):
    pruneColor(gramDict, bgc, shapeDescList)
    prunePoly(gramDict, shapeDescList)
    pruneGlobal(gramDict, shapeDescList)
    pruneAdj(gramDict, shapeDescList)
    pass

