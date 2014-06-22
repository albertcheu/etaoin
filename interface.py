import sys
from random import choice

from nltk.parse.chart import BottomUpLeftCornerChartParser as lcp
from nltk.data import load

from constants import N, SYMM, BASE, C, REGION, POLY, GENERICS, DEFNS
from filters import filterByNPSING, filterByNPPLUR, filterByPP, searchTree, treeHas, handleClose

def respond(output):
    print "Etta:", str(output)
    return

def handleBackground(bgc, tree):
    if treeHas(tree, 'BACKGROUND'):
        if treeHas(tree, 'C'):
            tf = bgc in col
            if treeHas(tree, 'QUESTION'): respond({True:'Yes',False:'No'}[tf])
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
    if len(filtered) == 0: response = "That doesn't exist"
    respond(response)
    pass

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
            hist = {}
            for shapeDesc in filtered:
                col = shapeDesc[C]
                if col not in hist: hist[col] = 1
                else: hist[col] += 1
                pass
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

def handleBool(tree, words, shapeDescList):
    if treeHas(tree, 'BOOLSING'):
        #Singular
        if treeHas(tree, 'THING'):
            filtered = filterByPP(tree, shapeDescList, shapeDescList)
            respond("Yes" if len(filtered) else "No, nothing")
            pass
        else:
            npsing = searchTree(tree, 'NPSING')[0]
            filtered = filterByNPSING(npsing, shapeDescList, shapeDescList)

            pass
        pass
    else:
        #Plural
        pass
    pass

def handleQuestion(tree, words, shapeDescList):
    if treeHas(tree, 'BOOLQ'): handlebool(tree, words, shapeDescList)
    elif treeHas(tree, 'COUNTQ'): handleCount(tree, words, shapeDescList)
    else: handleFetch(tree, words, shapeDescList)
    pass

def parseInput(parser, words, bgc, shapeDescList):
    #try:
    tree = parser.parse(words)
    #print 'Parsed properly'
    #print tree
    if not handleBackground(bgc, tree):
        if treeHas(tree,'ASSERTION'):handleAssertion(tree, words, shapeDescList)
        else: handleQuestion(tree, words, shapeDescList)
        pass
#except:
    #print sys.exc_info()
    #respond(choice(DUNNO)+" "+REASK)        
    pass

def interface(bgc, shapeDescList):
    respond("Ask me a question or assert a T/F statement")

    parser = lcp(load('file:grammar.cfg'))

    #Main loop
    while True:
        #Preprocess
        q = raw_input("You: ").strip("\n\t .?").lower()
        if "goodbye" in q: break
        if q.startswith("etta, "): q = q[6:]

        #Work on the words
        words = q.split()
        for i in range(len(words)):
            w = words[i]
            if w.endswith(","): words[i] = w[:-1]
            if w.endswith("'s"): words[i] = w[:-2]+" is"
            pass
        newords = []
        for w in words:
            for nw in w.split(): newords.append(nw)
            pass

        parseInput(parser, newords, bgc, shapeDescList)

        pass
    pass
