#!/usr/bin/python
from os import listdir
from pickle import load, dump
from copy import copy

def removeLabel(pointList, label):
    for i in range(len(pointList)):
        pt = pointList[i]
        (r,g,b,labels) = copy(pt)
        if label in labels: labels.remove(label)
        pointList[i] = (r,g,b,labels)
        pass
    pass

if __name__ == "__main__":
    fnames = sorted(listdir('colorCorpus'))
    for fname in fnames:
        pointList = load(open('colorCorpus/'+fname,'rb'))
        removeLabel(pointList, 'tan')
        dump(pointList, open('colorCorpus/'+fname,'wb'))
        pass
    pass
