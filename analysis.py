#!/usr/bin/python

from os import listdir

from gen import gen, getGramDict
from interface import interface,processWords
from constants import YES, NO, C, N
from imageAnalysis import processImage

def getSDLs(label):
    #label = 'good' or 'bad', the prefix of the filename in sceneInputs
    def complexity(shapeDescList):
    #Give a score of how complicated it is to describe the scene
        numFigures = len(shapeDescList)
        colorSet,typeSet = set(),set()
        for sD in shapeDescList:
            colorSet.add(sD[C])
            typeSet.add(sD[N])
            pass
        return numFigures+len(colorSet)+len(typeSet)

    sdlList = []
    #The 'complexity' of the simplest scene, the index of the simplest scene
    minComplexity,mindex = 1000,-1
    for i in range(1,7):
        fname = '%s%d'%(label,i)
        bgc,shapeDescList = processImage(fname+'.png')

        sdlList.append((bgc,shapeDescList))
        c = complexity(shapeDescList)
        if c < minComplexity: minComplexity,mindex = c, i-1
        pass
    return sdlList, mindex

def getTrueStatements(bgc, shapeDescList):
    #Build dictionary representation of the grammar
    gramDict = getGramDict(bgc, shapeDescList)
    #Use that grammar to make assertions about the scene (as rep. by the sDL)
    assertions = gen(gramDict,shapeDescList)
    #Get ready for the loop
    trueStatements,whole,nxt = [], len(assertions), 10
    for i in range(whole):
        tree = assertions[i]
        #Tell progress, as a percentage
        if int(float(i)*100/whole) == nxt:
            print nxt, 'percent of assertions processed'
            nxt += 10
            pass
        try:
            #Check each assertion if it is true
            #Only fetch the result we need, not the 'assertion' bool result
            ans = processWords(tree.leaves(),bgc,shapeDescList)[0]
            if ans == YES: trueStatements.append(' '.join(tree.leaves())+'\n')
            pass
        except:
            print tree.leaves()
            break
        pass
    return trueStatements

def getSharedTruths(ps, goodList, trueStatements):
    def match(words, sdlList, expected):
        #Do the words make up an assertion whose boolean value matches expected?
        for i in range(6):
            bgc, shapeDescList = sdlList[i]
            #Only fetch the result we need, not the 'assertion' bool result
            ans = processWords(words, bgc, shapeDescList)[0]
            if ans != expected: return False
            pass
        return True
    #Don't need to know the mindex of the bad pictures
    badList = getSDLs('problemSets/ps%d/bad'%ps)[0]
    sharedTruths = []
    for line in trueStatements:
        words = line.strip().split()
        if match(words,goodList,YES) and match(words,badList,NO):
            sharedTruths.append(line)
            pass
        pass
    return sharedTruths

def analyzeProblemSet(ps):
    goodList, mindex = getSDLs('problemSets/ps%d/good'%ps)

    print 'We shall generate true statements about good%d'%(mindex+1)
    #Background color and list of shape descriptors from the simplest scene
    bgc,shapeDescList = goodList[mindex]
    #Find assertions about the simplest scene
    trueStatements = getTrueStatements(bgc, shapeDescList)
    print 'There are',len(trueStatements),'true assertions'

    print 'How many are true for all six "good" images and false for all "bad"?'
    sharedTruths = getSharedTruths(ps, goodList,trueStatements)
    print len(sharedTruths)

    f = open('sharedTruths','w')
    f.writelines(sharedTruths)
    f.close()
    return 'There are %d statements true for the good images and false for the bad images:\n%s' % (len(sharedTruths),' '.join(sharedTruths))
