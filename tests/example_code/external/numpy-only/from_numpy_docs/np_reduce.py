from numpy import *
add.reduce(array([1.,2.,3.,4.])) # computes ((((1.)+2.)+3.)+4.)
# 10.0
multiply.reduce(array([1.,2.,3.,4.])) # works also with other operands. Computes ((((1.)*2.)*3.)*4.)
# 24.0
add.reduce(array([[1,2,3],[4,5,6]]), axis = 0) # reduce every column separately
# array([5, 7, 9])
add.reduce(array([[1,2,3],[4,5,6]]), axis = 1) # reduce every row separately
# array([ 6, 15])

