#!/usr/bin/python
from PIL import Image
from operator import le as convexDown
from operator import ge as convexUp
from math import sqrt, acos, pi
from random import sample
from sys import maxint
from bisect import bisect
from polygon import BoundingBox, DEFNS, inScreen
(X,Y) = (0,1)
MINDIST = 10
MINFRAC = 0.02

def edge(i, j, grid, height, width):
    if i > 0 and grid[i-1][j] != grid[i][j]: return True
    elif i < height-1 and grid[i+1][j] != grid[i][j]: return True
    elif j > 0 and grid[i][j-1] != grid[i][j]: return True
    elif j < width-1 and grid[i][j+1] != grid[i][j]: return True
    return False

def slope(pa, pb): return float(pa[Y] - pb[Y]) / (pa[X] - pb[X])

def smartInsert(half, currentElem, wrongConvexity):
    while len(half) > 1:
        (p1,p2,p3) = (half[-2], half[-1], currentElem)

        #Consider the triangle formed by p1, p2, & p3
        #If its shape is not what we want, we remove p2 from the hull
        #We repeat until we get the right shape

        #Find line between p1 and p3
        m = slope(p1,p3)

        #Check if p2 is above or below
        projectedY = p1[Y] + m * (p2[X] - p1[X])
        if wrongConvexity(p2[Y], projectedY): half.pop()
        else: break

        pass
    half.append(currentElem)
    pass

def makeHull(points):
    #Variant of Monotone Chain
    points.sort()

    #Make upper half
    upper = [points[0]]
    for i in range(1,len(points)):
        if points[i][X] == upper[-1][X]: upper.pop()
        smartInsert(upper, points[i], convexDown)
        pass
    #Make lower half
    lower = [points[-1]]
    for i in range(len(points)-2,-1,-1):
        if points[i][X] == lower[-1][X]: lower.pop()
        smartInsert(lower, points[i], convexUp)
        pass

    #Piece together (counter-clockwise from lower left)
    lower.reverse()
    if upper[-1] == lower[-1]: upper.pop()
    for i in range(len(upper)-1,-1,-1): lower.append(upper[i])
    if lower[-1] == lower[0]: lower.pop()

    return lower

def dist(p1, p2): return sqrt((p1[X]-p2[X])**2 + (p1[Y]-p2[Y])**2)

def angle(a,b,c):
    #Dot product
    dp = 0.0
    for i in range(2): dp += (b[i]-a[i])*(c[i]-b[i])
    (ab, bc) = (dist(a,b),dist(b,c))
    ratio = dp / (ab*bc)
    return acos(ratio)

def negligible(p1,p2,p3):
    #Is p2 very close to line p1-p3?
    if p1[X] == p3[X]: d = abs(p2[X]-p1[X])
    else:
        m = slope(p1,p3)
        #y = mx+i --> i = y-mx
        intercept = p1[Y]-(m*p1[X])
        #-mx+y-i = 0
        #ax+by+c = 0
        (a,b,c) = (-1*m,1,-1*intercept)
        d = abs(a*p2[X]+b*p2[Y]+c) / sqrt(a**2 + b**2)
        pass
    return d < MINFRAC * dist(p1, p3)
    #return angle(p1,p2,p3) < 0.1*pi or d < MINDIST
    #return d < MINDIST
    #return angle(p1,p2,p3) < 0.1*pi

def describe(edgePixels, swidth, sheight):
    #Make convex hull
    hull = makeHull(edgePixels)

    #Remove point clusters
    remove = set()
    for i in range(len(hull)):
        if dist(hull[i], hull[(i+1)%len(hull)]) < MINDIST: remove.add(hull[i])
        pass
    for item in remove: hull.remove(item)
    #print hull
    #Remove artifact pixels (in bitmap images, lines are bumpy)
    if len(hull) > 3:
        remove = set()
        (i,j,k) = (0,1,2)
        while i < len(hull):
            (p1,p2,p3) = (hull[i],hull[j],hull[k])
            if negligible(p1,p2,p3): remove.add(p2)
            else:
                if i > j: break
                i = j
                pass

            j = k
            k = (k+1)%len(hull)
            while hull[k] in remove and k < len(hull): k += 1
            pass

        for p in remove: hull.remove(p)
        pass
    print hull

    #What kind of polygon?
    kind = DEFNS[len(hull)]
    #Where is the polygon?
    bb = BoundingBox(hull, swidth, sheight)
    location = " ".join(bb.whereAmI())

    print "There is a", kind, "at the", location, "of the screen"
    pass

def explore(adj, unvisited):
    cc = []
    stack = [sample(unvisited, 1)[0]]
    while len(stack):
        p = stack[-1]
        stack.pop()
        if p in unvisited:
            cc.append(p)
            unvisited.remove(p)
            for neigh in adj[p]:
                if neigh in unvisited: stack.append(neigh)
                pass
            pass
        pass
    return cc

def connectedComponents(edgePixels, swidth, sheight):
    #Make adjacency list
    (unvisited, adj) = (set(),{})
    for (x,y) in edgePixels:
        adj[(x,y)] = []
        unvisited.add((x,y))
        for (dx,dy) in ((0,1),(0,-1),(1,0),(-1,0)):
            (nx, ny) = (x+dx,y+dy)
            loc = bisect(edgePixels, (nx,ny)) - 1
            if inScreen(nx,ny,swidth,sheight) and edgePixels[loc]==(nx,ny):
                adj[(x,y)].append((nx,ny))
                pass
            pass
        pass
    #Do a modified DFS
    ccs = []
    while len(unvisited): ccs.append(explore(adj, unvisited))
    return ccs

if __name__ == "__main__":
    im = Image.open("scene.png")
    pixels = list(im.getdata())
    (swidth, sheight) = im.size
    grid = []
    for row in range(sheight): grid.append([])
    for i in range(len(pixels)): grid[i/swidth].append(pixels[i])

    #Find pixels that are next to ones of different color
    edgePixels = []
    for x in range(swidth):
        for y in range(sheight):
            if edge(y,x,grid,sheight,swidth): edgePixels.append((x,y))
            pass
        pass

    #Describe each shape
    ccs = connectedComponents(edgePixels, swidth, sheight)
    for cc in ccs: describe(cc, swidth, sheight)

    pass
