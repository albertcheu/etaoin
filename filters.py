from Queue import Queue

from space import sameDesc
from constants import DUNNO, REASK, GENERICS, REVDEFNS, N, SYMM, BASE, C, REGION, POLY, SNUM

def searchTree(t, label):
    #Find the instances of the label (if nested, choose closest to root)
    q = Queue()
    q.put(t)
    ans = []
    while not q.empty():
        n = q.get()
        if type(n) != str:
            if n.node == label: ans.append(n)
            else:
                for child in n: q.put(child)
                pass
            pass
        pass
    return ans

def treeHas(tree, label): return len(searchTree(tree,label)) > 0

def filterByCN(cn, shapeDescList):
    #i.e. cn = ['green', 'octagon(s)'] or ['figure(s)']
    cn[-1] = cn[-1].rstrip('s')
    #just generic
    if len(cn)==1 and cn[0] in GENERICS: return shapeDescList
    ans = []
    for shapeDesc in shapeDescList:
        #just specific
        if len(cn) == 1 and shapeDesc[N] == REVDEFNS[cn[0]]:
            ans.append(shapeDesc)
            pass
        #C generic or C specific
        elif len(cn) > 1:
            sd = shapeDesc
            if cn[1] in GENERICS:
                if sd[C] == cn[0]: ans.append(sd)
                pass
            elif (sd[C], sd[N]) == (cn[0],REVDEFNS[cn[1]]):
                ans.append(sd)
                pass
            pass
        pass
    return ans

def adj(x,y):
    xr,yr = x[REGION],y[REGION]
    shareRow,shareCol = (xr/3 == yr/3),(xr%3 == yr%3)
    if shareRow ^ shareCol:
        if shareRow: return abs(xr%3 - yr%3)==1
        return abs(xr/3 - yr/3)==1
    return False

def below(a,b): return a[POLY].cy > b[POLY].maxY
def above(a,b): return a[POLY].cy < b[POLY].minY
def left(a,b): return a[POLY].cx < b[POLY].minX
def right(a,b): return a[POLY].cx > b[POLY].maxX

def satEnumP(enumTree, rel, relApp):
    #Given the tree for ENUMSING/PLUR, a list of shapeDescs (rel) that a noun phrase should be <relative to>, and the number of them that are (relApp), see if the number matches what the enum specifies
    #i.e. "above one X", "to the right of all X"
    #rel = X, relApp = no. of X that satisfy a relRule (above, to the right)
    if not enumTree or (enumTree.node=='ENUMPLUR' and enumTree.leaves()==['the']):
        return relApp > 0
    if treeHas(enumTree, 'NUM'): return SNUM[enumTree.leaves()[-1]]

    enumWords = ' '.join(enumTree.leaves())
    if enumWords in ('all','every','all other','each'):
        return relApp == len(rel)
    if 'not' in enumWords: return relApp != len(rel)
    if enumWords == 'all but one': return relApp == len(rel)-1
    if enumWords == 'no': return relApp == 0
    return relApp == 1

def filterByPP(ppTree, winnowed, shapeDescList):
    #From an already winnowed list, filter using prepositions
    #shapeDescList must be the whole/original listing of objects

    def filterByP1(tree, winnowed):
        #Simple case: global location (at the top of the screen, for example)
        ans = []
        loc = searchTree(tree, 'GLOBALLOC')[0].leaves()
        for shapeDesc in winnowed:
            #Find all instances within winnowed whose self-description matches
            poly = shapeDesc[POLY]
            w = poly.whereAmI()
            if sameDesc(loc, w): ans.append(shapeDesc)
            pass
        return ans

    def foo(ppsTree, nestedTree, label,
            cn, winnowed, relRule, shapeDescList, sans):
        #nestedTree is the subtree of ppsTree that has the noun phrase (cn)
        rel = filterByCN(cn, shapeDescList)
        if treeHas(ppsTree, 'P1'): rel = filterByP1(ppsTree,rel)

        #For every shape in winnowed, count those in rel that satisfy relRule
        d = mapByRelation(winnowed, rel, relRule)

        #Extract the enum, if any
        if treeHas(nestedTree,label):
            enumTree = searchTree(nestedTree,label)[0]
            pass
        else: enumTree = None

        #Go thru each entry and compare against rel's ENUM
        for shapeDesc,relApp in d.items():
            if satEnumP(enumTree,rel,relApp): sans.add(shapeDesc)
            pass

        pass

    def filterByPPS(ppsTree, winnowed, shapeDescList):
        #PPS -> P1 | P2
        
        #Relative location
        if treeHas(ppsTree, 'P2'):
            p2Tree = searchTree(ppsTree, 'P2')[0]
            #Determine the relRule
            if treeHas(p2Tree, 'ADJACENT'): relRule = adj
            else:
                if treeHas(p2Tree, 'HORIZ'):
                    relRule = {'left':left,'right':right}[p2Tree.leaves()[-2]]
                    pass
                elif p2Tree.leaves()[-1][0] == 'b': relRule = below
                else: relRule = above
                pass
            sans = set()
            #Handle case when we are relative to a plural phrase
            for npplur1 in searchTree(ppsTree,'NPPLUR1'):
                cn = searchTree(npplur1,'NPPLUR1SEC')[0].leaves()
                foo(ppsTree, npplur1, 'ENUMPLUR',
                    cn, winnowed, relRule, shapeDescList, sans)
                pass
            #Handle case when we are relative to a singular phrase
            #Not mutex with the earlier case
            #(i.e., above [triangles and a green figure])
            for npsing in searchTree(ppsTree, 'NPSINGSEC'):
                cn = searchTree(npsing, 'NPSINGTERT')[0].leaves()
                foo(ppsTree, npsing, 'ENUMSING',
                    cn, winnowed, relRule, shapeDescList, sans)
                pass
            ans = list(sans)
            pass
        
        #Global location
        else: ans = filterByP1(ppsTree, winnowed)

        return ans

    def mapByRelation(winnowed, rel, relRule):
        ans = {}
        for a in winnowed:
            ans[a] = 0
            for b in rel:
                if a!=b and relRule(a,b): ans[a] += 1
                pass
            pass
        return ans

    #First pass
    ppsTree = searchTree(ppTree, 'PPS')[0]
    ans = filterByPPS(ppsTree, winnowed, shapeDescList)

    #Recursive pass (possibly more than one preposition)
    for child in ppTree:
        if type(child) != str and child.node == 'PP':
            ans = filterByPP(child, ans, shapeDescList)
            break
        pass

    return ans

def handleClose(winnowed):
    #Treat pairs of figures that satisfy "next to" as edges
    #Find connected components larger than one
    def explore(winnowed, adjList, node, unvisited, cc):
        unvisited.remove(node)
        cc.append(winnowed[node])
        for neigh in adjList[node]:
            if neigh in unvisited:
                explore(adjList, neigh, unvisited)
                pass
            pass
        return

    n = len(winnowed)
    unvisited, adjList = set(), {}
    for i in range(n):
        unvisited.add(i)
        for j in range(n):
            adjList[i] = []
            if i != j and adj(winnowed[i],winnowed[j]): adjList[i].append(j)
            pass
        pass

    filtered = []
    while len(unvisited):
        cc = []
        node = sample(unvisited,1)[0]
        explore(winnowed, adjList, node, unvisited, cc)
        if len(cc) > 1: filtered += cc
        pass

    return filtered

def filterByNPSING(tree, winnowed, shapeDescList):
    #Iterate through shapeDescList and find the matching shape(s)
    nounTree = searchTree(tree, 'NPSING')[0]
    #C N | N
    nounSingTree = searchTree(tree, 'NPSINGTERT')[0]
    filtered = filterByCN(nounSingTree.leaves(), winnowed)
    if len(filtered) > 1 and treeHas(nounTree, 'PP'):
        filtered = filterByPP(searchTree(nounTree,'PP')[0],
                              filtered,shapeDescList)
        pass

    return filtered

def filterByNPPLUR(tree, winnowed, shapeDescList):
    pluralNounPhrase = searchTree(tree, 'NPPLURSEC')[0]
    #black figures, octagons, yellow pentagons, etc.
    if 'NPPLUR1' in pluralNounPhrase:
        cn = searchTree(pluralNounPhrase,'NPPLUR1SEC')[0]
        return filterByCN(cn.leaves(), winnowed)
    #otherwise, X and Y
    sfiltered = set()
    npplur1sec = searchTree(pluralNounPhrase,'NPPLUR1SEC')
    npsing = searchTree(pluralNounPhrase,'NPSING')
    for subtree in npplur1sec:
        sfiltered.update(set(filterByCN(subtree.leaves(),winnowed)))
        pass
    for subtree in npsing:
        sfiltered.update(set(filterByNPSING(subtree,winnowed)))
        pass
    if treeHas(tree,'PP'): filtered = filterByPP(tree, list(sfiltered), shapeDescList)
    else: filtered = list(sfiltered)
    return filtered
