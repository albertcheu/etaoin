from math import log as ln
from constants import COUNT, MINSLICE, THRESHOLD

def log_2(x): return ln(x) / ln(2)

def entropy(p):
    #Return the entropy of a Boolean r.v. that has a p chance of success
    if p in (0.0, 1.0): return 0.0
    q = 1 - p
    return -1 * (p*log_2(p) + q*log_2(q))

def findBounds(col, axis, n, numPos):
    #Find the left and right edges of the chunk of color (a slice of the cube)
    #Also determine size & entropy of slice
    (left, leftsize, right, rightsize) = (0, 0, 255, 0)
    while axis[left][col] == 0:
        leftsize += axis[left][COUNT]
        left += 1
        pass
    while axis[right][col] == 0:
        rightsize += axis[right][COUNT]
        right -= 1
        pass
    boundSize = n - (leftsize + rightsize)
    h = entropy(numPos / boundSize)
    return (left, right, boundSize, h)

def splitAxis(col, axis, n, numPos):
    #Find points along axis that give most informative splits
    #This means finding the points @ which gain ratio is greatest

    #numPos is the no. of points in the entire set that are <color>
    #n is the number of points in the entire set
    #h is the entropy of the color

    #Should split the slice containing target points, not anything outside
    (left, right, boundSize, h) = findBounds(col, axis, n, numPos)

    pts = splitRec(col, axis, numPos, left, right, boundSize, h)
    return pts, left, right

def splitRec(col, axis, numPos, left, right, boundSize, h):
    #Current no. of points & no. of positive results
    (leftSize,leftPos) = (0.0, 0.0)
    #Where to split & the gain from the split
    (loc, maxGain) = (0, 0.0)
    for i in range(left,right):
        leftSize += axis[i][COUNT]
        leftPos += axis[i][col]
        if i - left < MINSLICE: continue
        if right - i < MINSLICE: break
        leftProportion = leftPos / leftSize
        hLeft = entropy(leftProportion)

        rightSize = boundSize - leftSize
        rightPos = numPos - leftPos
        rightProportion = rightPos / rightSize
        hRight = entropy(rightProportion)
        
        #Information-theoretic computations
        remainder = (leftSize / boundSize) * hLeft
        remainder += (rightSize / boundSize) * hRight
        gain = h - remainder
        if remainder != 0.0 and gain > maxGain:
            (loc, maxGain) = (i, gain)
            q = [leftSize, leftPos, hLeft, rightSize, rightPos, hRight]
            pass
        pass

    #Measure how much we are able to learn from splitting
    gainRatio = maxGain / h
    #If it's negligible, do no split
    if gainRatio < THRESHOLD: return {}

    #Otherwise...
    [leftSize, leftPos, hLeft, rightSize, rightPos, hRight] = q
    #Recurse only if there is uncertainty & quite a few points
    if hLeft == 0 or leftPos < MINSLICE: lhs = {}
    else: lhs = splitRec(col, axis, leftPos, left, loc, leftSize, hLeft)
    if hRight == 0 or rightPos < MINSLICE: rhs = {}
    else: rhs = splitRec(col, axis, rightPos, loc+1, right, rightSize, hRight)
    #Give all the split points
    return {loc: (lhs, rhs)} if lhs or rhs else loc
