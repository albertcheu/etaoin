#!/usr/bin/python
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from os import listdir
from pickle import load

if __name__ == "__main__":
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    (exes,whys,zees) = ([],[],[])
    c = []
    fnames = listdir("./colorCorpus")
    for fname in fnames:
        data = load(open("./colorCorpus/"+fname,"rb"))
        for (r,g,b,colors) in data:
            if "tan" in colors:
                exes.append(r)
                whys.append(g)
                zees.append(b)
                c.append((r/255.0,g/255.0,b/255.0))
                pass
            pass
        pass
    ax.scatter(xs=exes,ys=whys,zs=zees,c=c)
    
    ax.set_xlim3d(0,255)
    ax.set_ylim3d(0,255)
    ax.set_zlim3d(0,255)
    plt.show()
    pass
