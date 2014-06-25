from random import choice

from constants import N, SYMM, BASE, C, REGION, POLY, GENERICS, DEFNS, SNUM, DNE, THEPROB, YES, NO
from filters import filterByNPSING, filterByNPPLUR, filterByPP, searchTree, treeHas, handleClose

def respond(output):
    print "Etta:", str(output)
    return

def handleBackground(bgc, tree):
    if treeHas(tree, 'BACKGROUND'):
        if treeHas(tree, 'C'):
            tf = bgc in col
            if treeHas(tree, 'QUESTION'): respond({True:YES,False:NO}[tf])
            else: respond(tf)
            pass
        else: respond(bgc)
        return True
    return False

def handleAssertion(tree, words, shapeDescList):
    respond("Can't do assertions yet, hold on.")
    pass

def handleFetch(tree, words, shapeDescList):
    fqTree = searchTree(tree, 'FETCHQ')[0]
    if treeHas(fqTree, 'FETCHQSING'):
        filtered = filterByNPSING(tree, shapeDescList, shapeDescList)
        pass
    elif 'are' in fqTree.leaves():
        filtered = filterByNPPLUR(tree, shapeDescList, shapeDescList)
        pass
    else:
        #print tree
        ppTree = searchTree(tree, 'PP')[0]
        filtered = filterByPP(ppTree, shapeDescList, shapeDescList)
        pass
    #print filtered

    response = ''
    for i in range(len(filtered)):
        shapeDesc = filtered[i]
        n = shapeDesc[N]
        polyType = DEFNS[n]
        loc = 'at the '+' '.join(shapeDesc[POLY].whereAmI())
        col = shapeDesc[C]

        if 'color' in words:
            response += ' '.join(('the',polyType,loc,'is',col))
            pass
        elif 'where' in words:
            response += ' '.join(('the',col,polyType,'is',loc))
            pass
        elif 'sides' in words:
            response += ' '.join(('the',col,choice(GENERICS),
                                  'has %d sides'%n))
            pass
        else: response += ' '.join(('the',col,polyType))

        if i < len(filtered)-1: response += ' and '

        pass
    if len(filtered) == 0: response = DNE
    respond(response)
    pass

def colorHistogram(winnowed):
    hist = {}
    for shapeDesc in winnowed:
        col = shapeDesc[C]
        if col not in hist: hist[col] = 1
        else: hist[col] += 1
        pass
    return hist

def handleCount(tree, words, shapeDescList):
    response = ''
    npplur = searchTree(tree, 'NPPLUR')[0]
    filtered = filterByNPPLUR(npplur, shapeDescList, shapeDescList)
    #print filtered
    if treeHas(tree, 'CQ1'):
        cq = searchTree(tree, 'CQ1')[0]
        if treeHas(cq, 'PP'): filtered = filterByPP(cq, filtered, shapeDescList)
        elif treeHas(cq, 'CLOSE'): filtered = handleClose(filtered)
        elif treeHas(cq, 'C'):
            f = []
            for shapeDesc in filtered:
                if shapeDesc[C] in cq.searchTree(cq,'C')[0].leaves():
                    f.append(shapeDesc)
                    pass
                pass
            filtered = f
            pass
        respond(len(filtered))
        pass
    else:
        cq = searchTree(tree, 'CQ2')[0]
        if not treeHas(cq, 'NP'):
            #same color as one another - make a histogram!
            hist = colorHistogram(filtered)
            response = ''
            for col in hist:
                if hist[col] > 1: response += str(hist[col])+' '+col+', '
                pass
            response.strip(' ,')
            respond(response if len(response) else 'None!')
            pass
        else:
            #same color as something else (NPPLUR or NPSING)
            ans = 0
            if treeHas(cq, 'NPPLUR'):
                rel = filterByNPPLUR(cq, shapeDescList, shapeDescList)
                sameCol = True
                col = rel[0][C]
                for shapeDesc in rel:
                    if shapeDesc[C] != col:
                        sameCol = False
                        break
                    pass
                if not sameCol: col = ''
                pass
            else:
                col = filterByNPSING(cq, shapeDescList, shapeDescList)[0][C]
                pass
            for shapeDesc in filtered:
                if shapeDesc[C] == col: ans += 1
                pass

            respond(ans)
            pass

        pass

    pass

def countTrue(winnowed, test):
    ans = 0
    for shapeDesc in winnowed:
        if test(shapeDesc): ans += 1
    return ans
def oneOrMore(winnowed, test): return countTrue(winnowed, test) >= 1
def applyAll(winnowed, test): return countTrue(winnowed, test) == len(winnowed)
def checkEnum(winnowed, test, n):return countTrue(winnowed, test) == n

def checkThe(npsing, winnowed):
    if npsing.leaves()[0] == 'the':
        if len(winnowed) > 1:
            respond(THEPROB)
            return False
        elif len(winnowed) == 0:
            respond(DNE)
            return False
        pass
    return True

def handleBool(tree, words, shapeDescList, sing):
    if treeHas(tree, 'THING'):
        #Is there something PP?
        filtered = filterByPP(tree, shapeDescList, shapeDescList)
        respond(YES if len(filtered) else NO)
        pass
    else:
        nphrase = searchTree(tree, 'NPSING' if sing else 'NPPLUR')[0]
        if sing: filtered = filterByNPSING(nphrase, shapeDescList,shapeDescList)
        else: filtered = filterByNPPLUR(nphrase, shapeDescList, shapeDescList)
        if treeHas(nphrase, 'NUM'):
            n = SNUM[searchTree(tree,'NUM')[0].leaves()[0]]
        else: n = None

        if 'does' in words or 'do' in words:
            if sing and not checkThe(nphrase, filtered): return
            if 'sides' in words:
                #does X have N sides?
                snum = searchTree(tree, 'NUM')[0].leaves()[0]
                matchSides = lambda sD: sD[N] == SNUM[snum]
                respond(YES if oneOrMore(filtered,matchSides) else NO)
                pass
            elif treeHas(tree, 'NP'):
                #do(es) X have the same color as NP? (X -> filtered)
                np = searchTree(tree, 'NP')[0]
                if np[0].node == 'NPSING': otherFiltered = filterByNPSING(np[0], shapeDescList, shapeDescList)
                else: otherFiltered = filterByNPPLUR(np[0], shapeDescList, shapeDescList)
                histList = colorHistogram(otherFiltered).keys()
                if len(histList) > 1:
                    np_words = " ".join(np[0].leaves())
                    respond(np_words+" don't have the same color to begin with")
                    pass
                else:
                    col = histList[0]
                    matchColor = lambda x: x[C] == col
                    singTest = oneOrMore(filtered,matchColor)
                    if n: plurTest = checkEnum(filtered,matchColor,n)
                    else: plurTest = applyAll(filtered,matchColor)
                    respond(YES if (sing and singTest) or plurTest else NO)
                    pass
                pass
            else:
                #Do X have the same color (as each other)?
                hist = colorHistogram(filtered)
                col = hist.keys()[0]
                plurTest = n == len(filtered) if n else len(filtered)==hist[col]
                respond(YES if plurTest else NO)
                pass
            pass
        elif 'there' in words:
            #Is there X?
            #<PP>, is/are there X?
            if type(tree[0]) != str:
                filtered = filterByPP(tree[0],filtered,shapeDescList)
                pass
            plurTest = len(filtered) if not n else len(filtered) == n
            respond(YES if plurTest else NO)
            pass
        elif tree[1].node == 'C':
            #Is/are X <color>?
            if sing and not checkThe(nphrase, filtered): return
            col = words[-1]
            if sing: test = oneOrMore(filtered,lambda sD:sD[C]==col)
            elif n: test = checkEnum(filtered,lambda sD:sD[C]==col, n)
            else: test = applyAll(filtered,lambda sD:sD[C]==col)
            respond(YES if test else NO)
            pass
        else:
            #Is/are X <an instance of Y>?
            #TO DO
            npsing = searchTree(tree[0], 'NPSING')[0]
            otherFiltered = filterByNPSING(npsing, shapeDescList, shapeDescList)
            if sing and not checkThe(npsing, otherFiltered): return
            ntrsct = set(filtered) & set(otherFiltered)
            singTest = len(ntrsct) and not n
            plurTest = len(ntrsct) == n
            respond(YES if singTest or plurTest else NO)
            pass
        pass
    pass

def handleQuestion(tree, words, shapeDescList):
    if treeHas(tree, 'BOOLQ'):
        sing = treeHas(tree, 'BOOLSING')
        subtree = searchTree(tree, 'BOOLSING' if sing else 'BOOLPLUR')[0]
        handleBool(subtree, words, shapeDescList, sing)
        
    elif treeHas(tree, 'COUNTQ'): handleCount(tree, words, shapeDescList)
    else: handleFetch(tree, words, shapeDescList)
    pass
