from numpy import *
def f(i,j):
    return i**2 + j**2
# ...
fromfunction(f, (3,3)) # evaluate functiom for all combinations of indices [0,1,2]x[0,1,2]
# array([[0, 1, 4],
#        [1, 2, 5],
#        [4, 5, 8]])

