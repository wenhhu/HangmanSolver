# HangmanSolver

## What is in package?

This is a python implementation of Hangman Solver. In our code, the most basic version of Hangman is adopted. To know more about this game, please check: https://en.wikipedia.org/wiki/Hangman_(game) .

You can find four source files in this package, `HangmanPlay.py`, `utilities.py`, `TestingScript.py` and `TestingScript_MPI.py`. The `utilities.py` contains all the tool functions and class to realize our strategy. The `TestingScript.py` and `TestingScript_MPI.py` are two scripts to test the accuracy and efficiency of our code. The latter is the corresponding MPI version. Before you use it, Please make sure a version of MPI and MPI4py are properly installed. The `HangmanPlay.py` is the playable script of this game.

## What is the strategy in this solver?
In general, there are three parts in our solver which handles different situations.

The first part is the "blind guessing" module. This module is used when we don't have any information about this word except for the length. As a result, we will select all the words with this length and take the most frequent letter in these words as our first guess. If it failed, we will narrow the candidates to those words which doesn't contain this letter and vice versa. If this letter is in the word, we will calculate the pattern number of this word corresponding to this letter. For instance, the pattern number of 'aaas' for 'a' is 1+2+4=7. By matching the pattern number of this word, we can narrow our candidates again. Note that, it's totally possible that the given word is not in our dictionary. Therefore, we will use a random module to handle this situation which we will talk about later. Otherwise, a regular guessing module will be used in the second stage.

The regular guessing module use a similar logic as "blind guessing" module to filter the candidate. We will keep searching for the most frequent but has not been check letter and take it as the next guess. If it is correct, the corresponding pattern number is calculated, which can be used to filter the candidates in our dictionary. According to our statistics, this part is the most time-consuming part in our program. To boost our calculation, we will calculate all the mask in the data loading stage. This is also a reason why data loading take a long time.

In the random guessing module, no information from the dictionary can be relied on. As a result, we can only randomly pick a letter which has not been checked. This should be the part we can improve on.

## Under Which version of python is this package coded?
Python 2.7

## How to use this solver?
`HangmanPlay.py`: ./HangmanPlay.py -i "path to dictionary"

`TestingScript.py`: ./TestingScript.py -i "path to dictionary"

`TestingScript_MPI.py`: ./TestingScript_MPI.py -i "path to dictionary"

In the `HangmanPlay.py` script, we will be required to provide the word you want our program to guess. By hitting enter, you can see the guess one by one.

## How to install MPI and MPI4py?
There are several popular MPI implementations currently. I strongly suggest you to install OpenMPI. You can get more information in their mainpages:

`OpenMPI`: https://www.open-mpi.org

Other MPI implementations can also be found in:

`MPICH`: http://www.mpich.org
`MVAPICH`: http://mvapich.cse.ohio-state.edu

Fortunately, you can skip this step if your os is ubuntu since openmpi is preinstalled in most distributions of ubuntu. If your os is OSX, you can install it on homebrew. On my machine, the command to install it is:

brew install open-mpi

MPI4py can be install easily with `pip` or `anaconda`. The commands are:

`pip install mpi4py`

`conda install -c mpi4py mpi4py=2.0.0`

For more information, please check:

http://pythonhosted.org/mpi4py/mpi4py.pdf

## Benchmark
Sequential:

|Number of Words| Correct Words | Accuracy | Loading Time| Calc. Time|Total Time|
|---------------|-----------|----------|-----|----|----|
|10000|9910|99.1%|6.5 s|19.1 s|25.6 s|
|50000|48300|96.6%|30.1 s|240 s| 270.1 s|
|250000|N/A|N/A|140 s|N/A| N/A|

MPI:

|Number of Words| Correct Words | Accuracy | Loading Time| Calc. Time|Total Time|
|---------------|-----------|----------|-----|----|----|
|10000|9910|99.1%|6.5 s|9.8 s|16.3 s|
|50000|48300|96.6%|32.1 s|120 s| 152.1 s|
|250000|N/A|N/A|150 s|N/A| N/A|

Specifications of testing machine:

Processor: 2.7 GHz Intel Core i5

Memory: 8 GB 1867 MHz DDR3

OS: MAC OSX 10.12
