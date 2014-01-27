import csv
import math

import matplotlib.pyplot as pplt
import numpy
from os import path

def make_plot():
    fpath = path.join('..', 'log.dat')
    f = csv.reader(open(fpath), delimiter=' ')
    #epoch time, OD1, OD2, state1, state2, u1, u2
    #coldat = ([],[],[],[],[],[],[])
    coldat = []

    count = 0
    for row in f:
        count = count+1
        if len(coldat) == 0:
            num_ch = (len(row)-1)/3
            coldat = [[] for q in range(len(row))]
            print 'found ' + str(num_ch) +' chambers'
        ind = 0
        for val in row:
            (coldat[ind]).append(float(val.strip('[],')))
            ind += 1
    
    tsec = numpy.array(coldat[0], dtype=numpy.float64)
    tsec = numpy.subtract(tsec,tsec[0])
    tmin = numpy.divide(tsec,numpy.ones(tsec.shape)*60)
    thr = numpy.divide(tmin,numpy.ones(tmin.shape)*60)
    tday = numpy.divide(thr,numpy.ones(thr.shape)*24)


    ind = 0
    pplt.figure(1)
    pplt.clf()
    while ind < num_ch:
        od = numpy.array(coldat[ind + 1], dtype=numpy.float64)
        z = numpy.array(coldat[num_ch + ind + 1])
        u = numpy.array(coldat[num_ch*2 + ind + 1])
        ind = ind + 1

        pplt.subplot(311)
        pplt.plot(thr, od)
        #pplt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
        #                            ncol=2, borderaxespad=0.)
        #pplt.legend([p1,p2],["chamber 1","chamber 2"], loc=8)
        pplt.ylim(0.10,0.35)
        pplt.ylabel('OD')
        pplt.subplot(312)
        pplt.plot(thr, u)
        pplt.ylabel('u')
        pplt.subplot(313)
        pplt.plot(thr,z,)
        pplt.ylabel('z')
        pplt.xlabel('hours')
    pplt.savefig('plot', dpy=300)

    print 'DONE!'


if __name__ == '__main__':
    make_plot()
