#!/usr/bin/python

from gen import gen, getGramDict
from interface import interface,processWords
from constants import YES, NO, C, N

from makeScene import makeScene1

#This file is what shall be called in the command-line

def complexity(shapeDescList):
    #Give a score of how complicated it is to describe the scene
    numFigures = len(shapeDescList)
    colorSet,typeSet = set(),set()
    for sD in shapeDescList:
        colorSet.add(sD[C])
        typeSet.add(sD[N])
        pass
    return numFigures+len(colorSet)+len(typeSet)

def getSDLs(label):
    #List of the shapeDescLists (technically, sDL's are tuples but who cares)
    metaList = []
    minComplexity,mindex = 1000,-1
    for i in range(1,7):
        fname = 'sceneInputs/%s%d'%(label,i)
        bgc,shapeDescList = makeScene1(fname)
        metaList.append((bgc,shapeDescList))
        c = complexity(shapeDescList)
        if c < minComplexity: minComplexity,mindex = c, i-1
        pass
    return metaList, mindex

def getTrueStatements(bgc, shapeDescList):
    gramDict = getGramDict(bgc, shapeDescList)
    assertions = gen(gramDict,shapeDescList)
    f = open('trueStatements','w')
    whole = len(assertions)
    nxt,numTrue = 10,0
    for i in range(whole):
        tree = assertions[i]
        if int(float(i)*100/whole) == nxt:
            print nxt, 'percent of assertions processed'
            nxt += 10
            pass
        try:
            ans, assertion = processWords(tree.leaves(),bgc,shapeDescList)
            if ans==YES:
                f.write(' '.join(tree.leaves())+'\n')
                numTrue += 1
                pass
            pass
        except:
            print tree.leaves()
            break
        pass
    f.close()
    print 'There are',numTrue,'true assertions'
    #interface(bgc, shapeDescList)
    pass

def getSharedTruths(metaList):
    def matchExpected(sdls, expected):
        for i in range(6):
            bgc, shapeDescList = sdls[i]
            ans, assertion = processWords(words, bgc, shapeDescList)
            if ans != expected: return False
            pass
        return True

    otherList, ignoreThisVar = getSDLs('bad')

    f = open('trueStatements')
    lines = f.readlines()
    f.close()
    sharedTruths = []
    for line in lines:
        words = line.strip().split()
        if matchExpected(metaList, YES) and matchExpected(otherList, NO):
            sharedTruths.append(line)
            pass
        pass
    return sharedTruths

if __name__ == "__main__":
    metaList, mindex = getSDLs('good')

    print 'We shall generate true statements about good%d'%(mindex+1)
    bgc,shapeDescList = metaList[mindex]
    getTrueStatements(bgc, shapeDescList)

    print 'How many are true for all six "good" images and false for all "bad"?'
    sharedTruths = getSharedTruths(metaList)
    print len(sharedTruths)

    f = open('trueStatements','w')
    f.writelines(sharedTruths)
    f.close()
    pass
