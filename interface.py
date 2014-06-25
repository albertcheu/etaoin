import sys

from nltk.parse.chart import BottomUpLeftCornerChartParser as lcp
from nltk.data import load

from filters import treeHas
from handlers import handleBackground, handleAssertion, handleQuestion, respond

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
