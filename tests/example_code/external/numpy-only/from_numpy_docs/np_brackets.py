from numpy import *
a = array([ [ 0, 1, 2, 3, 4],
    [10,11,12,13,14],
    [20,21,22,23,24],
    [30,31,32,33,34] ])

a[0,0] # indices start by zero
# 0
a[-1] # last row
# array([30, 31, 32, 33, 34])
a[1:3,1:4] # subarray
# array([[11, 12, 13],
#        [21, 22, 23]])

i = array([0,1,2,1]) # array of indices for the first axis
j = array([1,2,3,4]) # array of indices for the second axis
a[i,j]
# array([ 1, 12, 23, 14])

a[a<13] # boolean indexing
# array([ 0, 1, 2, 3, 4, 10, 11, 12])

b1 = array( [True,False,True,False] ) # boolean row selector
a[b1,:]
# array([[ 0, 1, 2, 3, 4],
#        [20, 21, 22, 23, 24]])

b2 = array( [False,True,True,False,True] ) # boolean column selector
a[:,b2]
# array([[ 1, 2, 4],
#        [11, 12, 14],
#        [21, 22, 24],
#        [31, 32, 34]])
