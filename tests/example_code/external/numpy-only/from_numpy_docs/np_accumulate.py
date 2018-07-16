from numpy import *
add.accumulate(array([1.,2.,3.,4.])) # like reduce() but also gives intermediate results
# array([ 1., 3., 6., 10.])
array([1., 1.+2., (1.+2.)+3., ((1.+2.)+3.)+4.]) # this is what it computed
# array([ 1., 3., 6., 10.])
multiply.accumulate(array([1.,2.,3.,4.])) # works also with other operands
# array([ 1., 2., 6., 24.])
array([1., 1.*2., (1.*2.)*3., ((1.*2.)*3.)*4.]) # this is what it computed
# array([ 1., 2., 6., 24.])
add.accumulate(array([[1,2,3],[4,5,6]]), axis = 0) # accumulate every column separately
# array([[1, 2, 3],
#        [5, 7, 9]])
add.accumulate(array([[1,2,3],[4,5,6]]), axis = 1) # accumulate every row separately
# array([[ 1, 3, 6],
#        [ 4, 9, 15]])

