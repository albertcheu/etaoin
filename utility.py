from Queue import Queue
from constants import N, SYMM, BASE, C, REGION, POLY, SNUM
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

def searchFirst(t, label): return searchTree(t,label)[0]

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

    enumWords = enumTree.leaves()
    #i.e. there are three polygons
    if treeHas(enumTree, 'NUM'): return SNUM[enumWords[-1]] == numSat

    #Except for one/two/.., all X ...
    if 'except' in enumWords:
        return numSat == len(winnowed) - SNUM[enumWords[-2]]

    #all other triangles; assumes the subject is singular
    #Technically wrong but fix later
    if 'other' in enumWords: return numSat == len(winnowed)-1

    #all/every/each shape(s)
    if enumWords[0] in ('all','every','each'): return numSat == len(winnowed)

    #Not all
    if 'not' in enumWords: return numSat != len(winnowed)

    #No X are Y
    if enumWords == ['no']: return numSat == 0

    if enumWords == ['one']: return numSat == 1

    #a/an shape
    return numSat >= 1
