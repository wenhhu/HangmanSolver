#!/usr/bin/env python

import csv
import time
import argparse
from utilities import *
from mpi4py import MPI

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Testing script')
    parser.add_argument('-i', type = str, help='path to dictionary file')
    args = parser.parse_args()

    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    num_process = comm.Get_size()

    start = time.time()
    data = []
    if rank==0:
        print "Loading dictionary, this process may take several minutes, please be patient... "
    with open(args.i) as file:
        reader = csv.reader(file)
        for row in reader:
            data.append(row[0])

    data = np.array(data)
    comp = data[0]

    ind, eff = 1, [0]
    for i in xrange(1, len(data)):
        if data[i]!=data[i-1]:
            eff.append(i)

    data = data[eff]
    Len = np.array([len(i) for i in data])
    length = max(Len)
    letters = [np.array([chr(i) in j for j in data]) for i in xrange(97, 123)]

    patterns = [[{} for j in xrange(26)] for i in xrange(length)]
    for l in xrange(length):
        for ind1, i in enumerate(letters):
            temp = data[(Len == l+1) & i]
            for ind2, j in enumerate(temp):
                rec = 0
                for ind3, k in enumerate(j):
                    if k == chr(ind1+97):
                        rec += (1<<ind3)

                if rec in patterns[l][ind1]:
                    patterns[l][ind1][rec].append(ind2)
                else:
                    patterns[l][ind1][rec] = [ind2]

    firstshot = [firstShot(data[Len==i+1]) for i in xrange(length)]
    filter = buildDataBase(data, Len, patterns, length, letters)

    if rank==0:
        print "Data loading is done, total time is %2f secs" % (time.time()-start)
        print "rank|count|accuracy|Tot. time|Ave. time"
        print "---------------------------------------"

    start = time.time()
    res = []
    comm.Barrier()
    count = 0
    i = rank

    while i < len(data):
        count += 1
        verify = Verifier(data[i], verbose = False)
        params = {'verify' : verify,
                  'patterns' : patterns,
                  'filter' : filter,
                  'firstshot' : firstshot,
                  'data' : data,
                  'Len' : Len,
                  'letters' : letters,
                  'playmode': False,
                  'chance' : 6}
        res.append(Guess(**params).tGuess())
        i += num_process
        if count % 1000 == 0:
            span = time.time()-start
            print rank, count, "  {:.2%}    {:.2f}    {:.4f}".format(sum(res)/float(len(res)), span, span/count)
    span = time.time()-start
    print rank, count, "  {:.2%}    {:.2f}    {:.4f}".format(sum(res)/float(len(res)), span, span/count)
    comm.Barrier()
    if rank==0:
        print "---------------------------------------"