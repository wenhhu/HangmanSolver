#!/usr/bin/env python

'''
This file is part of HangmanSolver, https://github.com/wenhhu/HangmanSolver, and is
Created on 03/12/2017
Contact: wenhao.baruch@gmail.com
Playable hangman script. Command:
./HangmanPlay.py -i "path to dictionary"
'''

import csv
import time
from utilities import *
import argparse

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
    print "Please input the word you want our program to guess:"

    while True:
        invalid = True
        words = ""
        while invalid:
            words = raw_input('>')
            if len(words)==0:
                continue
            invalid = False
            for i in words:
                if ord(i)<97 or ord(i)>123:
                    invalid = True
                    print "Invalid word, please input again!"
                    break

        verify = Verifier(words, verbose=False)
        # Input parameters of Guess constructor
        params = {'verify' : verify,
                 'patterns' : patterns,
                 'filter' : filter,
                 'firstshot' : firstshot,
                 'data' : data,
                 'Len' : Len,
                 'letters' : letters,
                 'playmode': True,
                 'chance': 6}
        guess = Guess(**params)
        print "{} missed:".format(' '.join(verify.ans))
        raw_input("Press Enter to continue...")
        guess.firstGuess()
        while guess.chance>0 and ('_' in verify.ans):
            guess.regGuess()
        if guess.chance<=0:
            print "failed"
        else:
            print "Bingo"

        pick = raw_input("Press Enter to continue...")