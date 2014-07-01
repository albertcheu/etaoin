from Queue import Queue
from math import sqrt
from constants import N, SYMM, BASE, C, REGION, POLY, SNUM, PADDING
def dist(a,b): return sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2)
def avg(a,b): return (a+b)/2.0

def adj(x,y):
    
    def oldAdj(x,y):
        xr,yr = x[REGION],y[REGION]
        shareRow,shareCol = (xr/3 == yr/3),(xr%3 == yr%3)
        if shareRow ^ shareCol:
            if shareRow: return abs(xr%3 - yr%3)==1
            return abs(xr/3 - yr/3)==1
        return False
    xp,yp = x[POLY],y[POLY]
    xr,yr = avg(xp.height,xp.width),avg(yp.height,yp.width)
    d = dist((xp.cx,xp.cy),(yp.cx,yp.cy))

    return d < (xr+yr) - PADDING or d < (xr+yr) + PADDING

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
