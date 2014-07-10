from constants import GENERICS, REVDEFNS, N, SYMM, BASE, C, REGION, POLY, SNUM
from utility import treeHas, searchTree, searchFirst, satEnum, adj, below, above, left, right

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

def filterByPP(ppTree, winnowed, shapeDescList):
    #From an already winnowed list, filter using prepositions
    #shapeDescList must be the whole/original listing of objects

    def filterByP1(tree, winnowed):
        #Simple case: global location (at the top of the screen, for example)
        ans = []
        loc = searchFirst(tree, 'GLOBALLOC').leaves()
        #Icky edge case for generating trees
        if ' ' in loc[-1]:
            cornerLoc = loc[-1].split()
            loc.pop()
            loc += cornerLoc
            pass
        for shapeDesc in winnowed:
            #Find all instances within winnowed whose self-description matches
            if shapeDesc[POLY].sameDesc(loc): ans.append(shapeDesc)
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
        if treeHas(nestedTree,label): enumTree = searchFirst(nestedTree,label)
        else: enumTree = None

        #Go thru each entry and compare against rel's ENUM
        for shapeDesc,relApp in d.items():
            if satEnum(enumTree,rel,relApp): sans.add(shapeDesc)
            pass

        pass

    def filterByPPS(ppsTree, winnowed, shapeDescList):
        #PPS -> P1 | P2
        
        #Relative location
        if treeHas(ppsTree, 'P2'):
            p2Tree = searchFirst(ppsTree, 'P2')
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
                cn = searchFirst(npplur1,'NPPLUR1SEC').leaves()
                foo(ppsTree, npplur1, 'ENUMPLUR',
                    cn, winnowed, relRule, shapeDescList, sans)
                pass
            #Handle case when we are relative to a singular phrase
            #Not mutex with the earlier case
            #(i.e., above [triangles and a green figure])
            for npsing in searchTree(ppsTree, 'NPSINGSEC'):
                cn = searchFirst(npsing, 'NPSINGTERT').leaves()
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
    for ppsTree in searchTree(ppTree, 'PPS'):
        ans = filterByPPS(ppsTree, winnowed, shapeDescList)
        winnowed = ans
        pass
    return ans

def handleAdjacent(winnowed):
    #Treat pairs of figures that satisfy "next to" as edges
    #Find connected components larger than one
    def explore(winnowed, adjList, node, unvisited, cc):
        unvisited.remove(node)
        cc.append(winnowed[node])
        for neigh in adjList[node]:
            if neigh in unvisited:
                explore(winnowed, adjList, neigh, unvisited, cc)
                pass
            pass
        return

    n = len(winnowed)
    unvisited, adjList = set(), {}
    for i in range(n):
        unvisited.add(i)
        adjList[i] = []
        for j in range(n):
            if i != j and adj(winnowed[i],winnowed[j]): adjList[i].append(j)
            pass
        pass

    filtered = []
    while len(unvisited):
        cc = []
        node = list(unvisited)[0]
        explore(winnowed, adjList, node, unvisited, cc)
        if len(cc) > 1: filtered += cc
        pass

    return filtered

def filterByNPSING(tree, winnowed, shapeDescList):
    #Iterate through shapeDescList and find the matching shape(s)
    nounTree = searchFirst(tree, 'NPSING')
    #C N | N
    nounSingTree = searchFirst(tree, 'NPSINGTERT')
    filtered = filterByCN(nounSingTree.leaves(), winnowed)
    if treeHas(nounTree, 'PP'):
        filtered = filterByPP(searchFirst(nounTree,'PP'),filtered,shapeDescList)
        pass
    return filtered

def filterByNPPLUR(tree, winnowed, shapeDescList):
    pluralNounPhrase = searchFirst(tree, 'NPPLURSEC')
    #black figures, octagons, yellow pentagons, etc.
    if 'NPPLUR1' in pluralNounPhrase:
        cn = searchFirst(pluralNounPhrase,'NPPLUR1SEC')
        sfiltered = set(filterByCN(cn.leaves(), winnowed))
    else:
    #otherwise, X and Y
        sfiltered = set()
        npplur1sec = searchTree(pluralNounPhrase,'NPPLUR1SEC')
        npsing = searchTree(pluralNounPhrase,'NPSING')
        for subtree in npplur1sec:
            sfiltered.update(set(filterByCN(subtree.leaves(),winnowed)))
            pass
        for subtree in npsing:
            sfiltered.update(set(filterByNPSING(subtree,winnowed,shapeDescList)))
            pass
        pass
    #print sfiltered
    if treeHas(tree,'PP'): filtered = filterByPP(tree, list(sfiltered), shapeDescList)
    else: filtered = list(sfiltered)
    #print filtered
    return filtered
