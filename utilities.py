#! /usr/bin/env python

'''
This file is part of HangmanSolver, https://github.com/wenhhu/HangmanSolver
Created on 03/12/2017
Contact: wenhao.baruch@gmail.com

In this module, we implemented all the tool functions needed for the handman solver, including data loading module, blind guessing module, regular guessing module and verifier module.
'''

import numpy as np
import random

def firstShot(d):
    ''' Build the blind guessing strategy.
    Args:
        d : array of scrubbed word with certain length in dictionary
    Return:
        best strategy of blind guessing
    '''
    chain = []
    if len(d)==0:
        return chain
    for chance in xrange(6):
        m = 0
        # Find the letter which has the highest frequency and take it as current answer
        for i in xrange(97,123):
            temp = np.array([chr(i) in j for j in d])
            m = max(sum(temp),m)
            if m == sum(temp):
                mask = temp
                l = chr(i)
        chain.append(l)
        # Use mask to pick the words which don't contain current letter, and in the loop, we will find the most frequent
        # letter in the new d.
        d = d[~mask]
        if len(d) == 0:
            break
    return chain

def buildDataBase(data, Len, patterns, length, letters):
    ''' Build the data base which is used in our strategy.
    Args:
        data: array of scrubbed word data
        Len: array storing the length of each word in data
        patterns: a data structure to store the indices of word with certain pattern numbers
        length: the length of the longest word in the dictionary
        letters: array storing the boolean index of word containing each letters

    Returns:
        a data structure to store the filtration logic in our strategy.
    '''
    filter = [[{} for j in xrange(26)] for i in xrange(length)]


    # Build filter which organize all the words according to their pattern number, length and letter.
    # For instance, we get retrieve the 5-letter words which contains letter 'a' with pattern number 4 by calling
    # filter[length-1][0][4]. Here, the pattern number is calculated by representing the word as a binary number which
    # take bit as 1 if current letter is on this bit. For instance, the 'a' pattern number of 'aaas' is 0111 which is
    # 7. In this way, we can narrow the candidates to a very large extent. After getting the words with above pattern,
    # we will sort them again according to the letter in them and associated pattern number which will end up with a list
    # of dictionary with length 26.

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
    '''class to encapsulate the unknown word, and provide utility to verify guesses.
    Attribute:
        _word (str): word to be guessed
        ans (str): current correct guesses
        verbose (boolean): a switch to control whether result should be shown in the form of message
    '''
    def __init__(self, word, verbose = True):
        self._word = word
        self.ans = np.array(["_"]*len(word))
        self.verbose = verbose

    def check(self, l):
        ''' Check whether input is in the word.
        Args:
            l: letter to be verified
        Return:
            return true if l is in the word.
        '''
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
        ''' Check whether all the letters in the word is guessed.
        Return:
            return true if word is correctly guessed
        '''
        return '_' in self.ans

    def reset(self):
        ''' Reset the guessed answer. '''
        self.ans = np.array(["_"]*len(self._word))

    def show(self):
        ''' Show the guessed answer so far. '''
        print("".join(self.ans))

class Guess():
    '''Class to conduct the guessing based on a degigned strategy
    Attribute:
        verify (verifier): "verifier" object which handles the verification of our guessing
        length (int): length of the word
        chance (int): number of chances to miss
        view (array): a list of candidates our program think the word can fall in
        mask (array of boolean index): the mask to pick possible candidates from "view"
        Len (array): array storing the length of each word in data
        patterns: a data structure to store the indices of word with certain pattern numbers
        indict (boolean): a boolean variable to determine whether this word is in our dictionary
        filter: a data structure to store the filtration logic in our strategy
        firstshot: best strategy of blind guessing
        playmode (boolean): switch controling whether interative mode of silent mode is used
        miss (list of index): list to store the missed guessing
    '''
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
        '''
        Initial blind guess based on the strategy we designed. Before we run out of guessing chances, return true if
        one letter is guessed.
        '''
        firstshot = self.firstshot
        for i in firstshot[self.length-1]:
            if self.chance<0:
                break
            self.last = i
            if self.verify.check(i):
                # if a letter is correctly guessed, we will narrow our candidates to the words stored in patterns.
                p = sum([1<<k for k, j in enumerate(self.verify.ans) if j != '_'])
                if p in self.filter[self.length-1][ord(i)-97]:
                    self.view = self.view[(self.Len == self.length) &
                                           self.letters[ord(i)-97]][self.patterns[self.length-1][ord(i)-97][p]]
                    self.filter = self.filter[self.length-1][ord(i)-97][p]
                    self.mask = np.array([True]*len(self.view))
                else:
                    # If the pattern number can't be found in our database, it means this word is not in our dictionary.
                    # As a result, we can only guess the letter randomly
                    self.indict = False
                if self.playmode:
                    self.display()
                return True
            else:
                self.miss.append(i)
                self.chance -= 1
                if self.playmode:
                    self.display()
        if self.chance > 0:
            self.indict = False
        return False

    def regGuess(self):
        ''' if one letter is guessed in the blind guessing phase, regular guessing strategy will be used instead.
        Return:
            True if current guess is right. Duplicate guess is regarded as wrong.
        '''
        if not self.indict:
            # If this word is not in our dictionary, we will randomly pick a letter which has not been checked.
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

        # If this word is in our dictionary, we need to find the most frequent but not checked letter in these words
        stat = [0]*26
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
            if l in self.verify.ans or l in self.miss:
                # If pattern number is not found, this word is confirmed not in our dictionary.
                self.indict = False
                return False
            self.chance -= 1
            self.miss.append(l)
            if 0 in self.filter[ord(l)-97]:
                # If every candidates contain this letter but this word doesn't, this word is not in our dict.
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
        ''' A function to combine the blind guess and regular guess
        Return:
            Return if word is fully guessed.
        '''
        if not self.firstGuess():
            return False

        # If guessing chance is not used up in the blind guessing stage, we will use regular guessing strategy
        while self.chance>0 and self.verify.done():
            self.regGuess()

        if self.chance>0:
            return True
        else:
            return False

    def display(self):
        ''' Display utility to be used in interactive mode'''
        print "guess :{}".format(self.last)
        print "{} missed: {}".format(' '.join(self.verify.ans), ','.join(self.miss))
        raw_input("Press Enter to continue...")