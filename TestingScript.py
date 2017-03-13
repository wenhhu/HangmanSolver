#!/usr/bin/env python
# This file is part of HangmanSolver, https://github.com/wenhhu/HangmanSolver, and is
# Created on 03/12/2017
# Contact: wenhao.baruch@gmail.com

'''
This is the script for testing the efficiency and correct rate of our program on the whole dictionary. In the command
line, the path of dictionary file need to be provided. An example of commands is:

./TestingScript.py -i words_50000.txt

The loading time is usually from 5 secs to 3 mins according to the size of dictionary. A dictionary with 500000 words
takes up to several mins according to my estimation.
'''

import csv
import time
import argparse
from utilities import *

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Testing script')
    parser.add_argument('-i', type = str, help='path to dictionary file')
    args = parser.parse_args()

    # Timer to record loading time
    start = time.time()
    data = []
    print "Loading dictionary, this process may take several minutes, please be patient... "
    with open(args.i) as file:
        reader = csv.reader(file)
        for row in reader:
            data.append(row[0])

    # Scrub the data by removing duplicates
    data = np.array(data)
    eff = [0]
    for i in xrange(1, len(data)):
        if data[i]!=data[i-1]:
            eff.append(i)

    data = data[eff]
    Len = np.array([len(i) for i in data])
    length = max(Len)

    # Sort the dictionary according to whether they contain a certain letter
    letters = [np.array([chr(i) in j for j in data]) for i in xrange(97, 123)]

    # Build the first filter to pick words with certain length, pattern and letters
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

    print "Data loading is done, total time is %2f secs" % (time.time()-start)

    # Timer to record calculation time
    start = time.time()

    res = []
    print "index|accuracy|Tot. time|Ave. time"
    print "----------------------------------"

    for ind, i in enumerate(data):
        verify = Verifier(i, verbose = False)
        # Input parameters of Guess constructor
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
        if ind % 1000 == 0 and ind!=0:
            span = time.time()-start
            print ind, "  {:.2%}    {:.2f}    {:.4f}".format(sum(res)/float(len(res)), span, span/(ind+1))
    span = time.time()-start
    print len(data), "  {:.2%}    {:.2f}    {:.4f}".format(sum(res)/float(len(res)), span, span/len(res))
    print "----------------------------------"