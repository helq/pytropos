from numpy import *
a = arange(6)
a = a.reshape(1,2,1,1,3,1)
a
# array([[[[[[0],
#            [1],
#            [2]]]],
#         [[[[3],
#            [4],
#            [5]]]]]])
a.squeeze() # result has shape 2x3, all dimensions with length 1 are removed
# array([[0, 1, 2],
#        [3, 4, 5]])
squeeze(a) # also exists

