import numpy as np
import random

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

def buildDataBase(data, Len, patterns, length, letters):
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
        self._word = word
        self.ans = np.array(["_"]*len(word))
        self.verbose = verbose

    def check(self, l):
        if l in self._word and l not in self.ans:
            if self.verbose:
                print("Effective pick!")
            pos = []
            for i in xrange(len(self._word)):
                if self._word[i] == l:
                    pos.append(i)
            self.ans[pos] = l
            return True
        else:
            if self.verbose:
                print("Failure, please try again.")
            return False

    def done(self):
        return '_' in self.ans

    def reset(self):
        self.ans = np.array(["_"]*len(self._word))

    def show(self):
        print("".join(self.ans))

class Guess():
    def __init__(self, **kwargs):
        self.verify = kwargs['verify']
        self.length = len(kwargs['verify'].ans)
        self.chance = kwargs['chance']
        self.view = kwargs['data']
        self.mask = None
        self.Len = kwargs['Len']
        self.patterns = kwargs['patterns']
        self.letters = kwargs['letters']
        self.indict = True
        self.filter = kwargs['filter']
        self.firstshot = kwargs['firstshot']
        self.playmode = kwargs['playmode']
        self.miss = []

    def firstGuess(self):
        firstshot = self.firstshot
        for i in firstshot[self.length-1]:
            if self.chance<0:
                break
            self.last = i
            if self.verify.check(i):
                p = sum([1<<k for k, j in enumerate(self.verify.ans) if j != '_'])
                if p in self.filter[self.length-1][ord(i)-97]:
                    self.view = self.view[(self.Len == self.length) & self.letters[ord(i)-97]][self.patterns[self.length-1][ord(i)-97][p]]
                    self.filter = self.filter[self.length-1][ord(i)-97][p]
                    self.mask = np.array([True]*len(self.view))
                else:
                    self.indict = False
                if self.playmode:
                    self.display()
                return True
            else:
                self.miss.append(i)
                self.chance -= 1
                if self.playmode:
                    self.display()
        return False

    def regGuess(self):
        if not self.indict:
            l = chr(random.choice([i for i in xrange(97, 123) if chr(i) not in self.verify.ans
                                                              and chr(i) not in self.miss]))
            self.last = l
            if not self.verify.check(l):
                self.chance -= 1
                self.miss.append(l)
                if self.playmode:
                    self.display()
                return False
            else:
                if self.playmode:
                    self.display()
                return True

        stat = [0]*26
        view = self.view
        filter = self.filter

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
            self.chance -= 1
            self.miss.append(l)
            if 0 in self.filter[ord(l)-97]:
                self.mask = self.mask & self.filter[ord(l)-97][0]
            else:
                self.indict = False
            if self.playmode:
                self.display()
            return False
        else:
            c = sum([1<<i for i, j in enumerate(self.verify.ans) if j == l])
            if c in self.filter[ord(l)-97]:
                self.mask = (self.mask & self.filter[ord(l)-97][c])
            else:
                self.indict = False
            if self.playmode:
                self.display()
            return True

    def tGuess(self):
        if not self.firstGuess():
            return False

        while self.chance>0 and self.verify.done():
            self.regGuess()

        if self.chance>0:
            return True
        else:
            return False

    def display(self):
        print "guess :{}".format(self.last)
        print "{} missed: {}".format(' '.join(self.verify.ans), ','.join(self.miss))
        raw_input("Press Enter to continue...")