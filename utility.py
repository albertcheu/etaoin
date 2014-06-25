from Queue import Queue

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

def respond(output):
    print "Etta:", str(output)
    return

def colorHistogram(winnowed):
    hist = {}
    for shapeDesc in winnowed:
        col = shapeDesc[C]
        if col not in hist: hist[col] = 1
        else: hist[col] += 1
        pass
    return hist

def satEnum(enumTree, winnowed, numSat):
    #Given the tree for ENUMSING/PLUR, a list of shapeDescs (wubbiwed), and the number of them that satisfy some condition (numSat), see if the number matches what the enum specifies
    if not enumTree or (enumTree.node=='ENUMPLUR' and enumTree.leaves()==['the']):
        return numSat > 0
    if treeHas(enumTree, 'NUM'): return SNUM[enumTree.leaves()[-1]]

    enumWords = ' '.join(enumTree.leaves())
    if enumWords in ('all','every','all other','each'):
        return numSat == len(winnowed)
    if 'not' in enumWords: return numSat != len(winnowed)
    if 'except' in enumWords: return numSat == len(winnowed)-1
    if enumWords == 'no': return numSat == 0
    return numSat >= 1
