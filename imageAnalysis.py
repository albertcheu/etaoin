#!/usr/bin/python
from math import sqrt, acos, pi, tan, atan2
from sys import maxint
from bisect import bisect

from PIL import Image, ImageColor

from polygon import Polygon, inScreen
from constants import DEFNS, COLORS, X,Y,MINDIST
from utility import dist, lineDist, slope
from color.treeMaker import belong
from pickle import load

def edge(bgTriple, i, j, grid, height, width):
    if grid[i][j] == bgTriple: return False
    for drow in (-1,0,1):
        for dcol in (-1,0,1):
            neigh = grid[i+drow][j+dcol]
            if grid[i][j] != neigh and neigh == bgTriple: return True
            pass
        pass
    return False

def removeClusters1(s):
    #Because bitmaps are made of little squares, angled lines are approximated
    #So there can be a pixel with the same yval as a triangle tip, for example
    #That artifact pixel is likely to be close to the tip
    ls = list(s)
    for i in range(len(ls)):
        for j in range(i+1,len(ls)):
            if dist(ls[i],ls[j]) < MINDIST and ls[j] in s: s.remove(ls[j])
            pass
        pass
    pass

def removeClusters2(s):
    def clockwise(ls):
        avgy = sum(pt[Y] for pt in ls) / len(ls)
        avgx = sum(pt[X] for pt in ls) / len(ls) 
        f = lambda pt: (atan2(pt[Y] - avgy, pt[X] - avgx) + 2*pi) % 2*pi
        ls.sort(key=f)
        pass
    def cycle(ls, s):
        i = 0
        while i < len(ls)-1:
            p1,p2,p3 = ls[i],ls[(i+1)%len(ls)],ls[(i+2)%len(ls)]
            if p1[X] == p3[X]: a,b,c = 1,0,-1*p1[X]
            else:
                m = slope(p1,p3)
                a,b,c = -1*m,1,m*p1[X]-p1[Y]
                pass
            if lineDist(a,b,c,p2) < MINDIST:
                s.remove(p2)
                i += 2
                pass
            else: i += 1
            pass
        pass
    #Because bitmaps are made of little squares, angled lines are approximated
    #So there can be a pixel with the same yval as a triangle tip, for example
    #That artifact pixel is likely to be close to the ideal line
    ls = list(s)
    clockwise(ls)
    cycle(ls,s)
    cycle(list(s),s)
    pass

def describe(edgePixels):
    #Only works because these are convex polygons whose vertices are always on the bounding box' sides

    def inRange(index, arr): return index > -1 and index < len(arr)

    def scanEdge(edgePixels, index, yval, inc1, inc2):
        while inRange(index, edgePixels) and edgePixels[index][Y] == yval:
            index += inc1
            pass
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

    removeClusters1(s)
    removeClusters2(s)

    ans = list(s)
    return ans

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
        cc.sort(key=lambda pt: (pt[Y],pt[X]))
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

def tripleToColor(colorTriple, decisionFunctions):
    (r,g,b) = colorTriple
    labels = []
    for col in decisionFunctions.keys():
        if decisionFunctions[col](r,g,b): labels.append(col)
        pass
    if len(labels) > 1:
        for col in ('orange','violet','cyan','tan','brown'):
            if col in labels: return col
            pass
        pass
    return labels[0]

def processImage(fname):
    im = Image.open(fname)
    pixels = list(im.getdata())
    (swidth, sheight) = im.size
    grid = []
    for row in range(sheight): grid.append([])
    for i in range(len(pixels)): grid[i/swidth].append(pixels[i])

    trees = load(open('color/decisionTrees.pkl','rb'))
    decisionFunctions = {}
    for col in COLORS: decisionFunctions[col] = belong(trees[col])

    #Find background color (RGB triple)
    bgTriple = grid[0][0]
    bgc = tripleToColor(bgTriple, decisionFunctions)

    #Find pixels that are next to ones of bgc
    edgePixels = []
    for j in range(swidth):
        for i in range(sheight):
            if edge(bgTriple, i,j,grid,sheight,swidth): edgePixels.append((j,i))
            pass
        pass

    ccs = connectedComponents(edgePixels, swidth, sheight)
    shapeDescList = []
    for cc in ccs:
        pts = describe(cc)
        n = len(pts)
        col,row = pts[0]
        cTriple = grid[row][col]
        c = tripleToColor(cTriple, decisionFunctions)
        poly = Polygon(pts,swidth,sheight)
        shapeDescList.append( (n, False,0, c, poly) )
        pass
    return bgc, shapeDescList
