from Queue import Queue
from math import sqrt
from constants import N, C, POLY, SNUM, PADDING, X,Y
def dist(a,b): return sqrt((a[X]-b[X])**2 + (a[Y]-b[Y])**2)
def avg(a,b): return (a+b)/2.0
def lineDist(a,b,c, pt): return abs(a*pt[X]+b*pt[Y]+c) / sqrt(a**2+b**2)
def slope(pa, pb): return float(pa[Y] - pb[Y]) / (pa[X] - pb[X])

def adj(a,b):
    apts,bpts = a[POLY].pts,b[POLY].pts
    #find closest pair of pts
    m = 1000
    pair = (None,None)
    for apt in apts:
        for bpt in bpts:
            if dist(apt,bpt) < m:
                m = dist(apt,bpt)
                pair = (apt,bpt)
                pass
            pass
        pass
    k = min(a[POLY].swidth,a[POLY].sheight)
    return m < k/3

def below(a,b): return a[POLY].cy > b[POLY].maxY and adj(a,b)
def above(a,b): return a[POLY].cy < b[POLY].minY and adj(a,b)
def left(a,b): return a[POLY].cx < b[POLY].minX and adj(a,b)
def right(a,b): return a[POLY].cx > b[POLY].maxX and adj(a,b)

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
    ans = "Etta: " + str(output)
    print ans
    return ans

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

    if not enumTree: return numSat > 0

    enumWords = enumTree.leaves()

    #The black polygon is at the right
    #There must be exactly 1 black polygon and it must be at the right
    if enumTree.node=='ENUMSING' and enumWords == ['the']:
        return numSat == 1 and len(winnowed) == 1

    #Except for one/two/.., all X are Y
    #Find the no. of X (len(winnowed)), and the no. of X that are Y (numSat)
    elif 'except' in enumWords:
        return numSat == len(winnowed) - SNUM[enumWords[-2]]

    #there are three polygons
    elif treeHas(enumTree, 'NUM'): return SNUM[enumWords[-1]] == numSat

    #the quadrilaterals (i.e. all quadrilaterals)
    #Should be a positive number of them
    elif enumWords == ['the']: return numSat > 0 and numSat == len(winnowed)

    #Not all
    elif 'not' in enumWords: return numSat != len(winnowed)

    #No X are Y; number of X that are Y is 0
    elif enumWords == ['no']: return numSat == 0

    elif enumWords == ['one']: return numSat == 1

    #an X; positive number of X
    return numSat > 0
