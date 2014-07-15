from random import randint, choice
from space import where, preprocess
from sys import maxint
from constants import MINFRACTION, TOP,RIGHT,BOTTOM,LEFT, DEFNS

#Triangles, rectangles/trapezoids, pentagons, hexagons

def inScreen(x, y, swidth, sheight):
    return x > -1 and x < swidth and y > -1 and y < sheight

def pickPtOnSide(side, leftBound, rightBound, upBound, lowBound, full=True):
    #Pick a point that lies on a side of the Box defined by the bounds
    #If not full, only pick from the first half of the side
    if side in (TOP, BOTTOM):
        width = rightBound - leftBound
        gap = width / MINFRACTION
        if full: x = randint(leftBound+gap, rightBound-gap)
        else: x = randint(leftBound+gap, (leftBound+width/2)-gap)
        y = upBound if side==TOP else lowBound
        pass
    else:
        height = lowBound - upBound
        gap = height / MINFRACTION
        x = leftBound if side == LEFT else rightBound
        if full: y = randint(upBound+gap,lowBound-gap)
        else: y = randint(upBound+gap, (upBound+height/2)-gap)
        pass
    return (x,y)

def makeBase(base, leftBound, rightBound, upBound, lowBound):
    (x0, y0) = pickPtOnSide(base, leftBound, rightBound,
                            upBound, lowBound, False)
    if base in (TOP, BOTTOM): (x1, y1) = (rightBound - (x0 - leftBound), y0)
    else: (x1, y1) = (x0, lowBound - (y0 - upBound))
    return [(x0, y0), (x1, y1)]

def makeTri(isos, base, leftBound, rightBound, upBound, lowBound):
    #Return 3 noncollinear points (which define a triangle)
    pts = []
    if isos:
        #Put the base on a side of the Box
        pts = makeBase(base, leftBound, rightBound, upBound, lowBound)
        #Get midpoint of other side
        other = {TOP:BOTTOM,LEFT:RIGHT,RIGHT:LEFT,BOTTOM:TOP}[base]
        (midX, midY) = ((leftBound+rightBound)/2, (lowBound+upBound)/2)
        tip = {TOP:(midX,upBound),BOTTOM:(midX,lowBound),
               LEFT:(leftBound,midY),RIGHT:(rightBound,midY)}[other]
        pts.append(tip)
        pass
    else:
        #Random scalene: pick three of the box's sides & pick points
        skip = choice((TOP,RIGHT,BOTTOM,LEFT))
        for side in (TOP,RIGHT,BOTTOM,LEFT):
            if side != skip:
                pt = pickPtOnSide(side,leftBound,rightBound,upBound,lowBound)
                pts.append(pt)
                pass
            pass
        pass

    return pts

def reflectBase(base, pts, leftBound, rightBound, upBound, lowBound):
    [(x0,y0),(x1,y1)] = pts
    if base in (TOP, BOTTOM):
        y2 = y3 = lowBound if base==TOP else upBound
        (x3, x2) = (x0, x1)
        pass
    else:
        x2 = x3 = rightBound if base == LEFT else leftBound
        (y3, y2) = (y0, y1)
        pass
    return [(x2,y2),(x3,y3)]

def makeQuad(rect, base, leftBound, rightBound, upBound, lowBound):
    #We need one side on a side of the Box
    pts = makeBase(base, leftBound, rightBound, upBound, lowBound)

    #Rectangle or trapezoid
    if rect:
        #Just reflect the base
        pts += reflectBase(base, pts, leftBound, rightBound, upBound, lowBound)
        pass
    else:
        #Make another base
        other = {TOP:BOTTOM,LEFT:RIGHT,RIGHT:LEFT,BOTTOM:TOP}[base]
        rem = makeBase(other, leftBound, rightBound, upBound, lowBound)
        rem.reverse()
        pts += rem
        pass

    return pts


def gen2(symm, aSide, bSide, leftBound, rightBound, upBound, lowBound):
    #The first new point
    (xa,ya) = pickPtOnSide(aSide, leftBound, rightBound, upBound, lowBound)
    #The second new point
    if symm: (xb,yb) = {TOP:(xa,upBound),LEFT:(leftBound,ya),
                        RIGHT:(rightBound,ya),BOTTOM:(xa,lowBound)}[bSide]
    else: (xb,yb) = pickPtOnSide(bSide,leftBound, rightBound, upBound, lowBound)
    return ((xa,ya),(xb,yb))

def makePent(symm, base, leftBound, rightBound, upBound, lowBound):
    #Our pentagons are going to be isosceles triangles with 2 more points
    pts = makeTri(True, base, leftBound, rightBound, upBound, lowBound)
    (x,y) = pts[-1]
    pts.pop()
    #Which sides the new points are on
    (aSide, bSide) = {BOTTOM:(LEFT,RIGHT),RIGHT:(TOP,BOTTOM),
                      LEFT:(TOP,BOTTOM),TOP:(LEFT,RIGHT)}[base]
    #(aSide, bSide) = {TOP:(LEFT,RIGHT),LEFT:(TOP,BOTTOM),
    #RIGHT:(TOP,BOTTOM),BOTTOM:(LEFT,RIGHT)}[loc]

    ((x3,y3),(x4,y4)) = gen2(symm, aSide, bSide, leftBound,
                             rightBound, upBound, lowBound)
    
    #Funny order to ensure it is rendered properly (need a cycle)
    pts = [(x,y),(x3,y3)] + pts + [(x4,y4)]
    return pts

def makeHex(symm, base, leftBound, rightBound, upBound, lowBound):
    #Hexagon = rect/trap + 2 points
    pts = makeQuad(choice((True,False)), base, leftBound, rightBound,
                   upBound, lowBound)
    #(x,y) = pts[0]
    #loc = where(x, y, leftBound, rightBound, upBound, lowBound)
    (aSide,bSide) = {TOP:(RIGHT,LEFT),LEFT:(BOTTOM,TOP),
                     BOTTOM:(RIGHT,LEFT),RIGHT:(BOTTOM,TOP)}[base]
    ((x4,y4),(x5,y5)) = gen2(symm, aSide, bSide, leftBound,
                             rightBound, upBound, lowBound)
    return pts[:2] + [(x4,y4)] + pts[2:] + [(x5,y5)]

def makeOct(symm, base, leftBound, rightBound, upBound, lowBound):
    if symm:
        #A "symm" octagon is two rectangles
        pts = makeQuad(True, base, leftBound, rightBound, upBound, lowBound)
        #(x,y) = pts[0]
        #loc = where(x, y, leftBound, rightBound, upBound, lowBound)
        otherBase = {TOP:RIGHT,LEFT:BOTTOM,BOTTOM:RIGHT,RIGHT:BOTTOM}[base]

        side1 = makeBase(otherBase, leftBound, rightBound, upBound, lowBound)

        if base in (BOTTOM, RIGHT): side1.reverse()
        side2 = reflectBase(otherBase,side1,leftBound,rightBound,
                            upBound,lowBound)

        pts = pts[:2] + side1 + pts[2:] + side2
        pass
    else:
        #Otherwise make four bases
        pts = []
        for base in (TOP,RIGHT,BOTTOM,LEFT):
            s = makeBase(base,leftBound,rightBound,upBound,lowBound)
            if base in (BOTTOM,LEFT): s.reverse()
            pts += s
            pass
        pass
    return pts

def inPoly(x, y, pts):
        #Given coordinates and a polygon (a list of points in cycle),
        #is the point in the polygon?
    def cross(o, a, b):
        cp = (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
        if cp == 0: return 0
        elif cp > 0: return 1
        return -1
    sign = cross((x,y),pts[0],pts[1])
    for i in range(1,len(pts)):
        cp = cross((x,y),pts[i],pts[(i+1)%len(pts)])
        if 0 not in (cp, sign) and cp != sign: return False
        if cp != 0: sign = cp
        pass
    return True

class Polygon():
    def __init__(self, pts, swidth, sheight):
        self.pts = pts
        self.swidth, self.sheight = swidth, sheight

        self.minX, self.minY, self.maxX, self.maxY = maxint,maxint,-1,-1
        for (x,y) in pts:
            if x < self.minX: self.minX = x
            if x > self.maxX: self.maxX = x
            
            if y < self.minY: self.minY = y
            if y > self.maxY: self.maxY = y
            pass
        self.width, self.height = (self.maxX-self.minX, self.maxY-self.minY)
        #Center of the bounding box
        (self.cx, self.cy) = ((self.minX+self.maxX)/2,(self.minY+self.maxY)/2)
        pass
    def translate(self, tx, ty):
        for i in range(len(self.pts)):
            (x,y) = self.pts[i]
            (x,y) = (x+tx,y+ty)
            self.pts[i] = (x,y)
            pass
        (self.minX, self.maxX) = (self.minX+tx, self.maxX+tx)
        (self.minY, self.maxY) = (self.minY+ty, self.maxY+ty)
        (self.cx, self.cy) = ((self.minX+self.maxX)/2,(self.minY+self.maxY)/2)
        pass
    
    def whereAmI(self):
        desc = where(self.sheight, self.swidth, self.cy, self.cx)
        return desc

    def sameDesc(self, loc):
        #Check if what a person types in (loc) is equivalent to where we are
        #Preprocess
        preprocess(loc)
        w = self.whereAmI()
        preprocess(w)
        if len(loc) == 1 and loc[0] in w: return True        
        return loc == w
