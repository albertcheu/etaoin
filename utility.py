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
    if enumWords == 'no': return relApp == 0
    return relApp == 1
