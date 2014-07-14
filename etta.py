#!/usr/bin/python

from gen import gen, getGramDict
from interface import interface,processWords
from constants import YES

from makeScene import makeScene1

#This file is what shall be called in the command-line

if __name__ == "__main__":
    bgc,shapeDescList = makeScene1('sceneInput')

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
