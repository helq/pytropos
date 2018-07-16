from numpy import *
tri(3,4,k=0,dtype=float) # 3x4 matrix of Floats, triangular, the k=0-th diagonal and below is 1, the upper part is 0
# array([[ 1., 0., 0., 0.],
#        [ 1., 1., 0., 0.],
#        [ 1., 1., 1., 0.]])
tri(3,4,k=1,dtype=int)
# array([[1, 1, 0, 0],
#        [1, 1, 1, 0],
#        [1, 1, 1, 1]])

