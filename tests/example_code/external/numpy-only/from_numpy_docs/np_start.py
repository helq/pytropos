from numpy import *
a = arange(12)
a = a.reshape(3,2,2)
print(a)
# [[[ 0  1]
#   [ 2  3]]
#  [[ 4  5]
#   [ 6  7]]
#  [[ 8  9]
#   [10 11]]]
a[...,0]                               # same as a[:,:,0]
# array([[ 0,  2],
#        [ 4,  6],
#        [ 8, 10]])
a[1:,...] # same as a[1:,:,:] or just a[1:]
# array([[[ 4, 5],
#         [ 6, 7]],
#        [[ 8, 9],
#         [10, 11]]])
