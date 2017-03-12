import csv
import numpy as np
import time
import random
import argparse

def firstShot(d):
    chain = []
    if len(d)==0:
        return chain
    for chance in xrange(6):
        m = 0
        for i in xrange(97,123):
            temp = np.array([chr(i) in j for j in d])
            m = max(sum(temp),m)
            if m == sum(temp):
                mask = temp
                l = chr(i)
        chain.append(l)
        d = d[~mask]
        if len(d) == 0:
            break
    return chain

def buildDataBase(data, Len, length, letters):
    filter = [[{} for j in xrange(26)] for i in xrange(length)]
    for l in xrange(length):
        for i in xrange(26):
            for p in patterns[l][i]:
                temp = data[(Len==l+1) & letters[i]][patterns[l][i][p]]
                cur = [{} for j in xrange(26)]
                for ind1, j in enumerate(temp):
                    rec = {}
                    for ind2, k in enumerate(j):
                        if type(rec.get(k))==int:
                            rec[k] += (1<<ind2)
                        elif k!=chr(i+97):
                            rec[k] = (1<<ind2)
                    for k in xrange(26):
                        if k!=i:
                            if chr(k+97) in rec:
                                if rec[chr(k+97)] in cur[k]:
                                    cur[k][rec[chr(k+97)]][ind1] = True
                                else:
                                    cur[k][rec[chr(k+97)]] = np.array([False]*temp.shape[0])
                                    cur[k][rec[chr(k+97)]][ind1] = True
                            else:
                                if 0 in cur[k]:
                                    cur[k][0][ind1] = True
                                else:
                                    cur[k][0] = np.array([False]*temp.shape[0])
                                    cur[k][0][ind1] = True

                filter[l][i][p] = cur
    return filter

class Verifier():
    def __init__(self, word, verbose = True):
        self.word = word
        self.ans = np.array(["_"]*len(word))
        self.verbose = verbose

    def check(self, l):
        if l in self.ans:
            # if self.verbose:
            #     print("This letter is checked already, pick another letter!")

            return False
        elif l in self.word:
            if self.verbose:
                print("Effective pick!")
            pos = []
            for i in xrange(len(self.word)):
                if self.word[i] == l:
                    pos.append(i)
            self.ans[pos] = l
            return True
        else:
            if self.verbose:
                print("Failure, please try again.")
            return False

    def reset(self):
        self.ans = np.array(["_"]*len(self.word))

    def show(self):
        print("".join(self.ans))

class Guess():
    def __init__(self, verify, filter):
        self.verify = verify
        self.length = len(verify.word)
        self.chance = 6
        self.view = None
        self.mask = None
        self.indict = True
        self.filter = filter
        self.miss = []

    def firstGuess(self):
        for i in firstshot[self.length-1]:
            self.last = i
            if self.verify.check(i):
                p = sum([1<<k for k, j in enumerate(self.verify.ans) if j != '_'])
                if p in self.filter[self.length-1][ord(i)-97]:
                    self.view = data[(Len == self.length) & letters[ord(i)-97]][patterns[self.length-1][ord(i)-97][p]]
                    self.filter = self.filter[self.length-1][ord(i)-97][p]
                self.mask = np.array([True]*len(self.view))
                return True
            else:
                self.miss.append(i)
                self.chance -= 1
        return False

    def regGuess(self):
        if not self.indict:
            l = chr(random.choice([i for i in xrange(97, 123) if chr(i) not in self.verify.ans and chr(i) not in self.miss]))
            self.last = l
            if not self.verify.check(l):
                self.chance -= 1
                self.miss.append(l)
                return False
            else:
                return True

        stat = [0]*26
        filter = self.filter
        view = self.view

        for i in view[self.mask]:
            temp = set()
            for j in i:
                if j not in self.verify.ans and j not in self.miss:
                    temp.add(j)
            for j in temp:
                stat[ord(j)-97] += 1
        l = chr(np.argmax(stat)+97)
        self.last = l
        if not self.verify.check(l):
            if l in self.verify.ans:
                self.indict = False
                return False
            self.miss.append(l)
            self.mask = self.mask & filter[ord(l)-97][0]
            self.chance -= 1
            return False
        else:
            c = sum([1<<i for i, j in enumerate(self.verify.ans) if j == l])
            if c in filter[ord(l)-97]:
                self.mask = (self.mask & filter[ord(l)-97][c])
            else:
                self.indict = False
            return True

    def tGuess(self):
        if not self.firstGuess():
            return False
        while self.chance>0 and '_' in self.verify.ans:
            self.regGuess()

        if self.chance>0:
            return True
        else:
            return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Testing script')
    parser.add_argument('-i', type = str, help='path to dictionary file')
    args = parser.parse_args()

    start = time.time()
    data = []
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
    filter = buildDataBase(data, Len, length, letters)

    print "Data loading is done, total time is %2f secs" % (time.time()-start)
    print "Please input the word you want our program to guess:"

    while True:
        invalid = True
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
        guess = Guess(verify, filter)
        print "{} missed:".format(' '.join(verify.ans))

        while guess.chance>0 and not guess.firstGuess():
            print "guess: {}".format(guess.last)
            print "{} missed: {}".format(' '.join(verify.ans), ','.join(guess.miss))
            raw_input("Press Enter to continue...")

        while guess.chance>0 and ('_' in verify.ans):
            print "guess :{}".format(guess.last)
            print "{} missed: {}".format(' '.join(verify.ans), ','.join(guess.miss))
            raw_input("Press Enter to continue...")
            guess.regGuess()

        print "guess: {}".format(guess.last)
        print "{} missed: {}".format(' '.join(verify.ans), ','.join(guess.miss))

        if guess.chance<=0:
            print "failed"
        else:
            print "Bingo"

        raw_input("Press Enter to continue...")