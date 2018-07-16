from numpy import *
a = array([[1,2],[5,8]])
a
# array([[1, 2],
#        [5, 8]])
m = matrix('1 2; 5 8')
m
# matrix([[1, 2],
#        [5, 8]])
asanyarray(a) # the array a is returned unmodified
# array([[1, 2],
#        [5, 8]])
asanyarray(m) # the matrix m is returned unmodified
# matrix([[1, 2],
#        [5, 8]])
asanyarray([1,2,3]) # a new array is constructed from the list
# array([1, 2, 3])

