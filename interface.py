import sys

from nltk.parse.chart import BottomUpLeftCornerChartParser as lcp
from nltk.data import load

from constants import NUMS, REASK, NO, YES
from utility import treeHas, searchFirst, respond
from handlers import handleBackground, handleAssertion, handleQuestion

PARSER = lcp(load('file:grammar.cfg'))

def parseInput(words, bgc, shapeDescList):
    try:
        tree = PARSER.parse(words)
        #print tree
        pass
    except:
        respond(REASK)
        print sys.exc_info()
        return

    #Assertions are answered with bool
    #Questions are answered with str

    #If the sentence has 'background', the handler returns a string
    #Otherwise, it returns False (bool)

    #Easiest type of question/assertion is about the background color
    x = handleBackground(bgc, tree)
    a = treeHas(tree,'ASSERTION')
    #Not about background
    if not x:
        #Rephrase the sentence into a question
        if a:
            words = handleAssertion(searchFirst(tree,'ASSERTION'),
                                    words, shapeDescList)
            tree = PARSER.parse(words)
            pass
        #Answer the question
        ans = handleQuestion(tree, words, shapeDescList)
        return ans, a
    #About background
    return x, a

def processWords(words, bgc, shapeDescList):
    for i in range(len(words)):
        w = words[i]
        if w.endswith(","): words[i] = w[:-1]
        if w.endswith("'s"): words[i] = w[:-2]+" is"
        if w.isdigit(): words[i] = NUMS[int(w)]
        pass
    newords = []
    for w in words:
        for nw in w.split(): newords.append(nw)
        pass

    return parseInput(newords, bgc, shapeDescList)

def interface(bgc, shapeDescList):
    respond("Ask me a question or assert a T/F statement")

    #Main loop
    while True:
        #Preprocess
        q = raw_input("You: ").strip("\n\t .?").lower()
        if "goodbye" in q: break
        if q.startswith("etta, "): q = q[6:]

        #Work on the words
        words = q.split()
        ans, assertion = processWords(words, bgc, shapeDescList)
        respond(ans)        
        pass
    pass
