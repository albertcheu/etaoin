from random import choice

from constants import N, SYMM, BASE, C, REGION, POLY, GENERICS, DEFNS, SNUM, DNE, THEPROB, YES, NO
from filters import filterByNPSING, filterByNPPLUR, filterByPP, handleClose
from utility import treeHas, searchFirst, respond, colorHistogram, satEnum

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
    #Rephrase the assertion as a boolean question!
    if treeHas(tree, 'NA'):
        #X is/are <remainder of sentence>
        naTree,rem = tree[0],tree[-1]
        nounPhrase = naTree[0][0]
        verb = naTree[0][-1]
        #is/are X <rem>?
        return [verb] + nounPhrase.leaves() + rem.leaves()
    elif treeHas(tree, 'NQ'):
        #there is/are X
        nqTree = tree[-1]
        verb, nounPhrase = nqTree[0][0], nqTree[0][-1]
        #is/are there X?
        return [verb, 'there'] + nounPhrase.leaves()
    elif treeHas(tree, 'ASSNCOL'):
        #X has the same color (as NP/each other)
        return

    #num sides

    return

def handleFetch(tree, words, shapeDescList):
    fqTree = searchFirst(tree, 'FETCHQ')
    if treeHas(fqTree, 'FETCHQSING'):
        filtered = filterByNPSING(tree, shapeDescList, shapeDescList)
        pass
    elif 'are' in fqTree.leaves():
        filtered = filterByNPPLUR(tree, shapeDescList, shapeDescList)
        pass
    else:
        #print tree
        ppTree = searchFirst(tree, 'PP')
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

def handleCount(tree, words, shapeDescList):
    response = ''
    npplur = searchFirst(tree, 'NPPLUR')
    filtered = filterByNPPLUR(npplur, shapeDescList, shapeDescList)
    #print filtered
    if treeHas(tree, 'CQ1'):
        cq = searchFirst(tree, 'CQ1')
        if treeHas(cq, 'PP'): filtered = filterByPP(cq, filtered, shapeDescList)
        elif treeHas(cq, 'CLOSE'): filtered = handleClose(filtered)
        elif treeHas(cq, 'C'):
            f = []
            for shapeDesc in filtered:
                if shapeDesc[C] in searchFirst(cq,'C').leaves():
                    f.append(shapeDesc)
                    pass
                pass
            filtered = f
            pass
        respond(len(filtered))
        pass
    else:
        cq = searchFirst(tree, 'CQ2')
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
        label,enumLabel=('NPSING','ENUMSING') if sing else ('NPPLUR','ENUMPLUR')
        nphrase = searchFirst(tree, label)
        enumTree = searchFirst(tree,enumLabel) if treeHas(tree, enumLabel) else None
        if sing: filtered = filterByNPSING(nphrase, shapeDescList,shapeDescList)
        else: filtered = filterByNPPLUR(nphrase, shapeDescList, shapeDescList)

        if 'does' in words or 'do' in words:
            if sing and not checkThe(nphrase, filtered): return
            if 'sides' in words:
                #does X have N sides?
                snum = searchFirst(tree, 'NUM').leaves()[0]
                matchSides = lambda sD: sD[N] == SNUM[snum]
                numSat = countTrue(filtered,matchSides)
                respond(YES if satEnum(enumTree, filtered, numSat) else NO)
                pass
            elif treeHas(tree, 'NP'):
                #do(es) X have the same color as NP? (X -> filtered)
                np = searchFirst(tree, 'NP')
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
                    numSat = countTrue(filtered, matchColor)
                    respond(YES if satEnum(enumTree, filtered, numSat) else NO)
                    pass
                pass
            else:
                #Do X have the same color (as each other)?
                hist = colorHistogram(filtered)
                col = hist.keys()[0]
                numSat = countTrue(filtered, lambda sD: sD[C] == col)
                respond(YES if satEnum(enumTree, filtered, numSat) else NO)
                pass
            pass
        elif 'there' in words:
            #Is/Are there X?
            #<PP>, is/are there X?
            if type(tree[0]) != str:
                filtered = filterByPP(tree[0],filtered,shapeDescList)
                pass
            respond(YES if len(filtered)  else NO)
            pass
        elif tree[1].node == 'C':
            #Is/are X <color>?
            if sing and not checkThe(nphrase, filtered): return
            col = words[-1]
            numSat = countTrue(filtered, lambda sD:sD[C]==col)
            respond(YES if satEnum(enumTree, filtered, numSat) else NO)
            pass
        elif treeHas(tree, 'UNITE'):
            #Are X close to one another? (i.e. 5 X, all X)
            numSat = len(handleClose(filtered))
            respond(YES if satEnum(enumTree, filtered, numSat) else NO)
            pass
        elif tree[-1].node == 'PP':
            #i.e. is X at the right? are Y below Z?
            newFiltered = filterByPP(tree[-1], filtered, shapeDescList)
            numSat = len(newFiltered)
            respond(YES if satEnum(enumTree, filtered, numSat) else NO)
            pass
        else:
            #Is/are X <instance(s) of Y>?
            respond("TO DO")
            pass
        pass
    pass

def handleQuestion(tree, words, shapeDescList):
    if treeHas(tree, 'BOOLQ'):
        sing = treeHas(tree, 'BOOLSING')
        subtree = searchFirst(tree, 'BOOLSING' if sing else 'BOOLPLUR')
        handleBool(subtree, words, shapeDescList, sing)
        
    elif treeHas(tree, 'COUNTQ'): handleCount(tree, words, shapeDescList)
    else: handleFetch(tree, words, shapeDescList)
    pass
