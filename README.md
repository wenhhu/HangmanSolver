# HangmanSolver

## What is in package?

This is a python implementation of Hangman Solver. In our code, the most basic version of Hangman is adopted. To know more about this game, please check: https://en.wikipedia.org/wiki/Hangman_(game)

You can find three source files in this package, `utilities.py`, `TestingScript.py` and `TestingScript_MPI.py`. The `utilities.py` contains all the tool functions and class to realize our strategy. The `TestingScript.py` and `TestingScript_MPI.py` are two scripts to test the accuracy and efficiency of our code. The latter is the corresponding MPI version. Before you use it, Please make sure a version of MPI and MPI4py are properly installed.

## What is the strategy in this solver?
In general, there are three parts in our solver which handles different situations.

The first part is the "blind guessing" module. This module is used when we don't have any information about this word except for the length. As a result, we will select all the words with this length and take the most frequent letter in these words as our first guess. If it failed, we will narrow the candidates to those words which doesn't contain this letter and vice versa. If this letter is in the word, we will calculate the pattern number of this word corresponding to this letter. For instance, the pattern number of 'aaas' for 'a' is 1+2+4=7. By matching the pattern number of this word, we can narrow our candidates again. Note that, it's totally possible that the given word is not in our dictionary. Therefore, we will use a random module to handle this situation which we will talk about later. Otherwise, a regular guessing module will be used in the second stage.



## How to use this solver?

## How to install MPI and MPI4py?
