#!/usr/bin/python
from PIL import Image
from operator import le as convexDown
from operator import ge as convexUp
from math import sqrt, acos, pi, tan
from sys import maxint
from bisect import bisect

from polygon import Polygon, inScreen
from constants import DEFNS

(X,Y) = (0,1)
MINDIST = 18
MINFRAC = 0.05

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

    #Piece together (clockwise from upper left)
    start = 0 if lower[0]!=upper[-1] else 1
    if lower[-1] == upper[0]: lower.pop()
    for i in range(start,len(lower)): upper.append(lower[i])

    return upper

def dist(p1, p2): return sqrt((p1[X]-p2[X])**2 + (p1[Y]-p2[Y])**2)

def angle(a,b,c):
    #Dot product
    dp = 0.0
    for i in range(2): dp += (b[i]-a[i])*(c[i]-b[i])
    (ab, bc) = (dist(a,b),dist(b,c))
    ratio = dp / (ab*bc)
    return acos(ratio)

def describe(edgePixels):
    #Only works because these are convex polygons whose vertices are always on the bounding box' sides

    def scanEdge(edgePixels, index, yval, inc1, inc2):
        while edgePixels[index][Y] == yval: index += inc1
        index += inc2
        return index

    s = set()
    #Top left, bottom right
    ytop,ybot = edgePixels[0][Y],edgePixels[-1][Y]
    s.add(edgePixels[0])
    s.add(edgePixels[-1])
    #
    topRight = scanEdge(edgePixels, 0, ytop, 1, -1)
    s.add(edgePixels[topRight])
    #
    bottomLeft = scanEdge(edgePixels, len(edgePixels)-1, ybot, -1, 1)
    s.add(edgePixels[bottomLeft])

    #Find leftmost and rightmost x
    leftx,rightx = 1000,-1
    for (x,y) in edgePixels:
        if x < leftx: leftx = x
        if x > rightx: rightx = x
        pass
    #The first instances are at the top
    unseenLeft, unseenRight = True, True
    prevLeft,prevRight = (0,0),(0,0)
    for (x,y) in edgePixels:
        if x == leftx:
            if unseenLeft:
                unseenLeft = False
                s.add((x,y))
                pass
            prevLeft = (x,y)
            pass
        elif x == rightx:
            if unseenRight:
                unseenRight = False
                s.add((x,y))
                pass
            prevRight = (x,y)
            pass
        pass

    #the last instances are at the bottom
    s.add(prevLeft)
    s.add(prevRight)

    #Remove point clusters
    ls = list(s)
    for i in range(len(ls)):
        for j in range(i+1,len(ls)):
            if dist(ls[i],ls[j]) < MINDIST and ls[j] in s: s.remove(ls[j])
            pass
        pass

    print len(s)
    print s
    print ytop,ybot,leftx,rightx
    return

def connectedComponents(edgePixels, swidth, sheight):
    def explore(adj, unvisited):
        #DFS code
        cc = []
        stack = [list(unvisited)[0]]
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
        cc.sort(key=lambda pt: pt[Y])
        return cc
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
    im = Image.open("problemSets/ps1/good6.png")
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
    for cc in ccs: describe(cc)

    pass
