#!/usr/bin/python

(LEFT, MIDDLE, RIGHT) = ("left", "middle", "right")
(TOP, BOTTOM) = ("top", "bottom")
(UPPER, LOWER) = ("upper", "lower")
CORNER = "corner"
OFFCENTER, CENTER = "off-center", "center"

def inBox(upBound, leftBound, lowBound, rightBound, row, col):
    if col < leftBound or col > rightBound: return False
    if row < upBound or row > lowBound: return False
    return True

#The point is at the ___ of the screen
def where(height, width, row, col):

    hor = ""
    (firstThirdH, secondThirdH) = (width / 3, 2*width / 3)
    if col < firstThirdH: hor = LEFT
    elif col < secondThirdH: hor = MIDDLE
    else: hor = RIGHT

    vert = ""
    (firstThirdV, secondThirdV) = (height / 3, 2*height / 3)
    if row < firstThirdV: vert = TOP
    elif row < secondThirdV: vert = MIDDLE
    else: vert = BOTTOM

    cornerSize = min(firstThirdH,firstThirdV)

    if hor == MIDDLE:
        if vert == MIDDLE: return [CENTER]
        elif vert == TOP: return [TOP]
        return [BOTTOM]

    #Upper left corner
    elif inBox(0,0,cornerSize,cornerSize,row,col):
        return [TOP,LEFT,CORNER]
    #Upper right corner
    elif inBox(0,width-cornerSize,cornerSize,width-1,row,col):
        return [TOP,RIGHT,CORNER]
    #Lower left corner
    elif inBox(height-cornerSize,0,height-1,cornerSize,row,col):
        return [BOTTOM,LEFT,CORNER]
    #Lower right corner
    elif inBox(height-cornerSize,width-cornerSize,height,width,row,col):
        return [BOTTOM,RIGHT,CORNER]
    
    if vert == MIDDLE:
        if hor == LEFT: return [LEFT]
        return [RIGHT]

    return [vert, hor]

def preprocess(desc):
    if CORNER in desc: desc.pop()
    if MIDDLE in desc: desc.remove(MIDDLE)
    if UPPER in desc: desc[desc.index(UPPER)] = TOP
    if LOWER in desc: desc[desc.index(LOWER)] = BOTTOM

def sameDesc(loc, w):
    #Check if what a person types in (loc) is equivalent to what the above function determined (w)
    
    #Preprocess
    preprocess(loc)
    preprocess(w)

    if len(loc) == 1 and loc[0] in w: return True

    return loc == w
