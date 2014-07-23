from random import randint, choice
from subprocess import call

from PIL import Image, ImageDraw

from constants import MINSWIDTH,MINSHEIGHT,MAXSWIDTH,MAXSHEIGHT,MINBWIDTH,MINBHEIGHT,MAXBWIDTH,MAXBHEIGHT, GRAYDIST,LEFTGRAY,RIGHTGRAY
from polygon import *
MAKERS = {3:makeTri,4:makeQuad,5:makePent,6:makeHex,8:makeOct}

def getRGB(c):
    def getRange(token):
        if '-' in token: return map(int, token.split('-'))
        if int(token) < 128: return 0,int(token)
        return int(token), 255

    #Given a color (string), return a matching tuple of RGB values
    if c == 'gray':
        r = randint(LEFTGRAY,RIGHTGRAY)
        g = randint(r-GRAYDIST,r+GRAYDIST)
        b = randint(r-GRAYDIST,r+GRAYDIST)
        return (r,g,b)

    f = open('color/ranges')
    lines = f.readlines()
    f.close()
    for line in lines:
        if c in line:
            #For each of (r,g,b), pick a random number within the given range
            tokens = line.strip().split()[1:]
            ans = []
            for token in tokens:
                left,right = getRange(token)
                ans.append(randint(left,right))
                pass
            return tuple(ans)
        pass

    #should never get here
    return (-1,-1,-1)

def makeScene2(bgc, shapeDescList, fname):
    (swidth,sheight) = (randint(MINSWIDTH,MAXSWIDTH),
                         randint(MINSHEIGHT,MAXSHEIGHT))
    
    #Make our "canvas", an image file
    im = Image.new("RGB", (swidth,sheight), bgc)
    draw = ImageDraw.Draw(im)

    (xthird, ythird) = (swidth / 3, sheight / 3)
    for i in range(len(shapeDescList)):
        
        (n, symm, base, c, region) = shapeDescList[i]

        #Make the polygon
        (bwidth, bheight) = (randint(MINBWIDTH,MAXBWIDTH),
                             randint(MINBHEIGHT,MAXBHEIGHT))
        maker = MAKERS[n]
        pts = maker(symm, base, 0,bwidth,0,bheight)
        polygon = Polygon(pts, swidth, sheight)
        polygon.translate(-1*polygon.minX, -1*polygon.minY)

        #Center the polygon in the region
        (x,y) = (xthird * (region % 3), ythird * (region / 3))
        (dx, dy) = ((xthird-polygon.width)/2,(ythird-polygon.height)/2)
        polygon.translate(x+dx,y+dy)

        draw.polygon(polygon.pts, 'rgb'+str(getRGB(c)))

        shapeDescList[i] = (n, symm, base, c, polygon)
        pass

    #Save scene
    im.save(fname+'.png')

    pass


def makeScene1(fname):
    f = open(fname)
    lines = f.readlines()
    f.close()
    #bgc
    #k
    #c_i
    #n_i
    #region_i
    
    l = 0
    bgc = lines[l].strip()
    l += 1
    k = int(lines[l].strip())
    l += 1

    shapeDescList = []
    for i in range(k):
        c = lines[l].strip()
        l += 1
        n = int(lines[l].strip())
        l += 1
        region = int(lines[l].strip())
        l += 1

        #Random for now
        symm = choice((True,False))
        base = choice((TOP,RIGHT,BOTTOM,LEFT))

        shapeDescList.append((n, symm, base, c, region))
        pass

    makeScene2(bgc, shapeDescList, fname)
    return bgc,shapeDescList
