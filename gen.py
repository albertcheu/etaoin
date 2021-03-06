QUOTE = "'"
PIPE = "|"

from copy import copy

from nltk.tree import Tree

from constants import N,C,POLY,REVDEFNS, COLORS
from utility import adj, left, right, above, below, treeHas,searchFirst,satEnum
from handlers import checkThe
from filters import filterByCN, filterByPP, filterByNPSING, filterByNPPLUR

def getGramDict(bgc, shapeDescList):
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
    prune(gramDict, bgc, shapeDescList)
    return gramDict

def buildDAG(gramDict, combos):
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
        if not haveProd:
            combos[production] = list(Tree(production, [x]) for x in gramDict[production])
            pass
        else: dag.append(production)
        pass
    dag = []
    explore('S', gramDict, combos, dag)
    return dag

def stitchPossibilities(production, item, combos):
    #type(item) in (str,list); if list, it is a list of Trees
    #This function finds all possible combinations of the sequence it describes
    #Each production has possibilites, stored in combos[prod...]

    def stitchRec(left, rightList, prod):
        #Left is either a list of Trees (an expanded nonterminal) or a str
        #rightList is a list of everything after left in 'item'
        #prod is the top-level production that starts the recursion

        #Base case: bottom of recursion
        if len(rightList) == 0:
            if type(left) == str: return [[left]]
            return left

        ans = stitchRec(rightList[0], rightList[1:],prod)
        newAns = []
        for i in range(len(ans)):
            t = [ans[i]] if type(ans[i])==Tree else ans[i]
            if type(left) == str: newAns.append([left]+t)
            else:
                #Nip tautologies in the bud! Also, don't say strange things
                for s in left:
                    if not (tautology(s,t[-1],prod) or badGram(s,t[-1],prod)):
                        newAns.append([s]+t)
                    pass
                pass
            pass
        return newAns

    def tautology(leftTree,rightTree, prod):
        #green X have the same color
        if prod == 'ASSNCOL' and treeHas(leftTree,'C'): return True
        #X near each other are near each other
        if prod == 'ADJASSN' and treeHas(rightTree,'ADJACENT'): return True
        #
        if prod == 'BASICASSN':
            #Green x are green
            if rightTree.node=='C': return treeHas(leftTree,'C')
            #
            elif leftTree.node=='NASEC':return False
            if treeHas(rightTree,'SPECIFICS') or treeHas(rightTree,'SPECIFICP'):
                #x triangle is a triangle
                label = 'NPSINGTERT' if leftTree.node=='NIS' else 'NPPLUR1SEC'
                ls = searchFirst(leftTree, label)
                rs = searchFirst(rightTree, label)
                return len(set(ls.leaves()) & set(rs.leaves())) > 0
            #X is/are polygon(s)
            return True

        #A triangle has three sides
        if prod == 'S':
            if rightTree.node == 'SIDES': return treeHas(leftTree,'SPECIFICS')
        return False
    def badGram(leftTree,rightTree,prod):
        if prod == 'BASICASSN':
            leftWord,rightWord = leftTree.leaves()[0],rightTree.leaves()[0]
            if treeHas(rightTree,'ENUMSING') or treeHas(rightTree,'ENUMPLUR'):
                #X is each Y
                #The figures at the left are all/except... X
                for tabooWord in ('one','all','except'):
                    if tabooWord == rightWord: return True
                    pass
                return 'the' == rightWord and 'the' != leftWord
                pass
            pass
        elif prod == 'S' and leftTree.node=='THERE':
            #There are (the X / all X / except for N all X)
            if treeHas(rightTree,'ENUMPLUR'):
                return not treeHas(rightTree, 'NUM')
            #There is (the X / each X)
            elif treeHas(rightTree,'ENUMSING'): return treeHas(rightTree, 'THE')
            pass
        return False

    l = list((combos[x] if x.isupper() else x) for x in item)
    ans = []
    for possibility in stitchRec(l[0], l[1:], production):
        ans.append(Tree(production,possibility))
        pass
    return ans

def gen(gramDict, shapeDescList):
    #Map each production to all the possible expansions of terminals
    #combos = mapping of str (a production) to list of trees
    #each tree is a possible instance of the production
    combos = {}
    combos['S'] = []
    dag = buildDAG(gramDict, combos)
    for production in dag:
        #Fill in combos[production]; guaranteed to have child productions!
        for item in gramDict[production]:
            #A sequence (i.e. C NSING)
            if type(item) == list:
                combos[production] += stitchPossibilities(production,
                                                          item, combos)
                pass
            #A plain production
            elif item.isupper():
                for possibility in combos[item]:
                    combos[production].append(Tree(production, [possibility]))
                    pass
                pass
            #A terminal
            else: combos[production].append(Tree(production,[item]))
            pass
        pruneCombos(production, combos, shapeDescList)
        print production, len(combos[production])
        pass
    return combos['S']

def pruneCombos(production, combos, shapeDescList):
    #post-pruning: eliminate combos of color and nouns that DNE
    if production in ('NPSINGTERT','NPPLUR1SEC'):
        newList = []
        for tree in combos[production]:
            if len(filterByCN(tree.leaves(),shapeDescList)) > 0:
                newList.append(tree)
                pass
            pass
        combos[production] = newList
        pass
    #eliminate combos of enumeration & nouns that DNE (i.e. five triangles)
    elif production in ('NPPLUR1','NPSINGSEC'):
        newList = []
        for tree in combos[production]:
            leaves = tree.leaves()
            x = len(leaves)-1
            cn = leaves[x:]
            if len(leaves) > 2 and leaves[-2] in COLORS: cn = leaves[x-1:]
            filtered = filterByCN(cn,shapeDescList)
            if len(filtered) > 0:
                enumTree = None
                if production == 'NPPLUR1' and treeHas(tree, 'ENUMPLUR'):
                    enumTree = searchFirst(tree,'ENUMPLUR')
                    pass
                elif production == 'NPSINGSEC' and treeHas(tree,'ENUMSING'):
                    enumTree = searchFirst(tree,'ENUMSING')
                    pass
                if satEnum(enumTree, filtered, len(filtered)):
                    newList.append(tree)
                    pass
                pass
            pass
        combos[production] = newList
        pass
    elif production == 'PPS':
        newList = []
        for tree in combos[production]:
            if len(filterByPP(Tree('PP',[tree]),shapeDescList,shapeDescList))>0:
                newList.append(tree)
                pass
            pass
        combos[production] = newList
        pass
    elif production in ('NPSING','NPPLUR'):
        newList = []
        sing = production=='NPSING'
        if sing: f,enumLabel=filterByNPSING,'ENUMSING'
        else: f,enumLabel=filterByNPPLUR,'ENUMPLUR'

        for tree in combos[production]:
            if treeHas(tree,enumLabel): enumTree = searchFirst(tree,enumLabel)
            else: enumTree = None
            filtered = f(tree,shapeDescList,shapeDescList)
            #The triangle: there must be exactly one
            if sing:
                errorResult,okay = checkThe(tree, filtered)
                if okay: newList.append(tree)
                pass

            #polygons: there must be more than one
            elif not enumTree and len(filtered) > 1: newList.append(tree)

            else:
                numSat = len(filtered)
                if satEnum(enumTree, filtered, numSat): newList.append(tree)
                pass
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
    if len(gramDict['SPECIFICS'])==0:del gramDict['SPECIFICS']
    if len(gramDict['SPECIFICP'])==0:del gramDict['SPECIFICP']
    pass

def pruneGlobal(gramDict, shapeDescList):
    #Get rid of global locations
    globalLocs = ['center','top','top left','top right','left','right','bottom','bottom left','bottom right']
    for i in range(len(gramDict['CORNERLOC'])):
        gramDict['CORNERLOC'][i] = ' '. join(gramDict['CORNERLOC'][i])
        pass

    for globalLoc in globalLocs:
        inList = False
        for shapeDesc in shapeDescList:
            if shapeDesc[POLY].sameDesc(globalLoc.split()):
                inList = True
                break
            pass
        if not inList:
            if globalLoc in gramDict['CORNERLOC']:
                gramDict['CORNERLOC'].remove(globalLoc)
                pass
            elif globalLoc in gramDict['HORIZ']:
                gramDict['HORIZ'].remove(globalLoc)
                pass
            elif globalLoc in gramDict['VERT']:
                gramDict['VERT'].remove(globalLoc)
                pass
            else: gramDict['GLOBALLOC'].remove(globalLoc)
        pass
    for loc in ('CORNERLOC','HORIZ','VERT'):
        if len(gramDict[loc]) == 0:
            del gramDict[loc]
            gramDict['GLOBALLOC'].remove(loc)
            pass
        pass
    if len(gramDict['GLOBALLOC'])==0: del gramDict['GLOBALLOC']
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
        del gramDict['ADJASSN']
        del gramDict['P2']
        del gramDict['ADJACENT']
        del gramDict['CARDINAL']
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

