from random import randint, choice
from subprocess import call

from PIL import Image, ImageDraw

from polygon import *
MAKERS = {3:makeTri,4:makeQuad,5:makePent,6:makeHex,8:makeOct}

#Min/max width & height of the screen
(MINSWIDTH, MINSHEIGHT) = (400, 400)
(MAXSWIDTH, MAXSHEIGHT) = (600, 600)

#Our polygons must be flush against a Box
#The Box's dimensions are bounded thusly
(MINBWIDTH, MINBHEIGHT) = (100, 100)
(MAXBWIDTH, MAXBHEIGHT) = (120, 120)

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

        #print polygon.width, polygon.height, polygon.pts
        draw.polygon(polygon.pts, c)

        shapeDescList[i] = (n, symm, base, c, polygon)
        pass

    #Save scene
    im.save(fname+'.png')

    #Show scene
    #call(["gnome-open",fname+'.png'])

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

        #Random symmetry & orientation for now
        symm = choice((True,False))
        base = choice((TOP,RIGHT,BOTTOM,LEFT))

        shapeDescList.append((n, symm, base, c, region))
        pass

    makeScene2(bgc, shapeDescList, fname)
    return bgc,shapeDescList
