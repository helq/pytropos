from numpy import *
a = arange(24).reshape(2,3,4) # a has 3 axes: 0,1 and 2
a
# array([[[ 0, 1, 2, 3],
#         [ 4, 5, 6, 7],
#         [ 8, 9, 10, 11]],
#        [[12, 13, 14, 15],
#         [16, 17, 18, 19],
#         [20, 21, 22, 23]]])
apply_over_axes(sum, a, [0,2]) # sum over all axes except axis=1, result has same shape as original
# array([[[ 60],
#         [ 92],
#         [124]]])

