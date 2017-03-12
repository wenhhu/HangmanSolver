import csv
import numpy as np
import time
import argparse
from mpi4py import MPI

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

def buildDataBase(data, Len, length, letters, patterns):
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
            if self.verbose:
                print("This letter is checked already, pick another letter!")
            return True
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
        self.filter = filter
        self.miss = []

    def firstGuess(self):
        for i in firstshot[self.length-1]:
            if self.verify.check(i):
                p = sum([1<<k for k, j in enumerate(self.verify.ans) if j != '_'])
                self.view = data[(Len == self.length) & letters[ord(i)-97]][patterns[self.length-1][ord(i)-97][p]]
                self.filter = self.filter[self.length-1][ord(i)-97][p]
                self.mask = np.array([True]*len(self.view))
                return True
            else:
                self.miss.append(l)
                self.chance -= 1
        return False

    def regGuess(self):
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
        if not self.verify.check(l):
            self.mask = self.mask & filter[ord(l)-97][0]
            self.miss.append(l)
            return False
        else:
            c = sum([1<<i for i, j in enumerate(self.verify.ans) if j == l])
            self.mask = self.mask & filter[ord(l)-97][c]
            return True

    def tGuess(self):
        if not self.firstGuess():
            return False
        while self.chance>0 and '_' in self.verify.ans:
            if not self.regGuess():
                self.chance -= 1
        if self.chance>0:
            return True
        else:
            return False

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
    filter = buildDataBase(data, Len, length, letters, patterns)

    if rank==0:
        print "Data loading is done, total time is %2f secs" % (time.time()-start)
        print "rank|index|accuracy|Tot. time|Ave. time"
        print "---------------------------------------"

    start = time.time()
    res = []
    comm.Barrier()
    count = 0
    i = rank

    while i < len(data):
        count += 1
        word = Verifier(data[i], verbose = False)
        res.append(Guess(word, filter).tGuess())
        i += num_process
        if count % 1000 == 0:
            span = time.time()-start
            print rank, count, "  {:.2%}    {:.2f}    {:.4f}".format(sum(res)/float(len(res)), span, span/count)
    span = time.time()-start
    print rank, count, "  {:.2%}    {:.2f}    {:.4f}".format(sum(res)/float(len(res)), span, span/count)
    comm.Barrier()
    if rank==0:
        print "---------------------------------------"