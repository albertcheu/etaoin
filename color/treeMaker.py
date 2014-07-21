#!/usr/bin/python
from os import listdir
from pickle import load, dump
from math import sqrt, exp

from split import splitAxis
from constants import COLORS, COUNT, THRESHOLD, A1,B1,A2,B2

def freqTable():
    #Map color label to integer
    ans = {}
    for col in COLORS: ans[col] = 0
    #Also have a handy counter of all points
    #One point may have more than 1 color
    ans[COUNT] = 0
    return ans

def axisTable():
    #A freqTable for every point along an axis
    #Makes (perpendicular-planar) splitting possible
    ans = []
    for i in range(256): ans.append(freqTable())
    return ans

def fillTables(colorCount, raxis, gaxis, baxis):
    (points, seen) = ([], set())
    fnames = listdir("./colorCorpus")
    for fname in fnames:
        data = load(open("./colorCorpus/"+fname,"rb"))
        for (r,g,b,colors) in data:
            if len(colors) == 0: continue
            
            if (r,g,b) not in seen:
                seen.add((r,g,b))
                points.append((r,g,b,colors))
                raxis[r][COUNT] += 1
                gaxis[g][COUNT] += 1
                baxis[b][COUNT] += 1
                pass
            else:
                for i in range(len(points)):
                    p = points[i]
                    if p[0]==r and p[1]==g and p[2]==b:

                        points[i] = (r,g,b, points[i][3]+colors)
                        break
                    pass
                pass

            for col in colors:
                #Each value of r,g,&b has a frequency table
                #Used to determine split points on each axis
                raxis[r][col] += 1
                gaxis[g][col] += 1
                baxis[b][col] += 1
                colorCount[col] += 1
                pass
            pass
        pass
    return points

def inBox(r, g, b, boxDef):
    ((redLeft,redRight), (greenLeft,greenRight), (blueLeft,blueRight)) = boxDef
    if r < redLeft or r > redRight: return False
    elif g < greenLeft or g > greenRight: return False
    elif b < blueLeft or b > blueRight: return False
    return True

def getSplit(splits):
    #Either an int or a dict; return a number & the next level
    if type(splits) is int: return splits, ({},{})
    elif type(splits) is dict and len(splits) > 0:
        splitPoint = splits.keys()[0]
        return splitPoint, splits[splitPoint]
    return None, None

def splitEdge(s, left, right):
    if s: return [(left,s), (s+1, right)]
    return [(left, right)]

def chi2dist(pt, deg):
    z = sqrt(pt) - sqrt(deg)
    if z <= 0: return 1 - 0.5 * exp(B1*z + A1*(z**2))
    return 0.5 * exp(B2*z + A2*(z**2))

def cutBox(col, t, box, redHalves, greenHalves, blueHalves, nextLevelRed, nextLevelGreen, nextLevelBlue, p):
    (numTrue, numFalse, numBool) = (0,0,0)
    #Try every box that results from applying the cuts
    for i in range(len(redHalves)):
        redHalf = redHalves[i]
        for j in range(len(greenHalves)):
            greenHalf = greenHalves[j]
            for k in range(len(blueHalves)):
                blueHalf = blueHalves[k]
                
                newBoxDef = (redHalf, greenHalf, blueHalf)
                nlr = None if not nextLevelRed else nextLevelRed[i]
                nlg = None if not nextLevelGreen else nextLevelGreen[j]
                nlb = None if not nextLevelBlue else nextLevelBlue[k]
                subtree = makeTreeRec(col, box, newBoxDef, nlr, nlg, nlb, p)
                if type(subtree) is bool:
                    numBool += 1
                    if subtree: numTrue += 1
                    else: numFalse += 1
                    pass
                t[newBoxDef] = subtree
                pass
            pass
        pass
    return (numTrue, numFalse, numBool)

def chi2prune(box, numPos, p, t):
    #proportion positive, proportion negative
    ppos = float(numPos) / len(box)
    pneg = 1 - ppos
    delta = 0
    for newBoxDef in t.keys():
        newBoxSize = 0
        for (r,g,b,colors) in box:
            if inBox(r,g,b,newBoxDef): newBoxSize+=1
            pass
        #expected proportion positive/negative
        if newBoxSize == 0: (eppos, epneg) = (ppos, pneg)
        else: (eppos, epneg) = (ppos * newBoxSize, pneg * newBoxSize)
        delta += ((ppos - eppos)**2 / eppos) + ((pneg - epneg)**2 / epneg)
        pass
    return p if chi2dist(delta, len(box)-1) < THRESHOLD else t

def makeTreeRec(col, points, boxDef, splitRed, splitGreen, splitBlue, p=True):
    #Gather all points in the box
    box = []
    numPos = 0
    for (r,g,b, colors) in points:
        if inBox(r,g,b, boxDef): box.append((r,g,b,colors))
        if col in colors: numPos += 1
        pass
    #If no points in box, return parent plurality
    if len(box) == 0: return p
    #If all points belong or all points do not belong, return the category
    elif numPos == len(box): return True
    elif numPos == 0: return False
    
    #Find applicable split planes
    (sRed, nextLevelRed) = getSplit(splitRed)
    (sGreen, nextLevelGreen) = getSplit(splitGreen)
    (sBlue, nextLevelBlue) = getSplit(splitBlue)

    #If there are none that cut this box, find plurality
    p = numPos > len(box) - numPos
    if not (sRed or sGreen or sBlue): return p
    
    #Else, split at least once (get 2,4, or 8 boxes)
    ((redLeft,redRight),(greenLeft,greenRight),(blueLeft,blueRight))=boxDef
    redHalves = splitEdge(sRed, redLeft, redRight)
    greenHalves = splitEdge(sGreen, greenLeft, greenRight)
    blueHalves = splitEdge(sBlue, blueLeft, blueRight)

    t = {}

    #Try every box that results from applying the cuts
    (numTrue, numFalse, numBool) = cutBox(col, t, box, redHalves, greenHalves, blueHalves, nextLevelRed, nextLevelGreen, nextLevelBlue, p)

    #If all children are leaves of the same bool val, no point in splitting
    if numTrue == len(t): return True
    elif numFalse == len(t): return False
    #All children are leaf nodes; do chi-squared pruning
    #elif numBool == len(t): return chi2prune(box, numPos, p, t)
    return t

def makeTree(col, raxis, gaxis, baxis, n, numPos, points):
    #Find bounding-box & split points within it
    (splitRed, redLeft, redRight) = splitAxis(col, raxis, n, numPos)
    (splitGreen, greenLeft, greenRight) = splitAxis(col, gaxis, n, numPos)
    (splitBlue, blueLeft, blueRight) = splitAxis(col, baxis, n, numPos)
    #print col, splitRed, splitGreen, splitBlue

    t = {}
    #Points within box must be split
    boxDef = ((redLeft,redRight), (greenLeft,greenRight), (blueLeft,blueRight))
    t[boxDef] = makeTreeRec(col,points,boxDef, splitRed, splitGreen, splitBlue)
    return t

def belong(tree):
    
    def decide(r, g, b):
        boxDef = tree.keys()[0]
        if not inBox(r,g,b, boxDef): return False
        return decideRec(r,g,b, tree[boxDef])
    
    def decideRec(r,g,b,tree):
        if type(tree) is bool: return tree
        for boxDef in tree.keys():
            if inBox(r,g,b, boxDef): return decideRec(r,g,b,tree[boxDef])
            pass
        return False

    return decide

if __name__ == "__main__":
    #Keep track of number of each color
    colorCount = freqTable()

    #Do the same for each value of r/g/b
    (raxis, gaxis, baxis) = (axisTable(),axisTable(),axisTable())

    #Fill in the tables
    points = fillTables(colorCount, raxis, gaxis, baxis)
    n = len(points)

    trees = {}
    for col in COLORS:
        #no. of positive data points (flagged with this color)
        numPos = float(colorCount[col])
        trees[col] = makeTree(col, raxis, gaxis, baxis, n, numPos, points)
        pass

    dump(trees, open("decisionTrees.pkl","wb"))

    pass
