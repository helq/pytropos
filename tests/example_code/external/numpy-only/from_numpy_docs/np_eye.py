from numpy import *
eye(3,4,0,dtype=float) # a 3x4 matrix containing zeros except for the 0th diagonal that contains ones
# array([[ 1., 0., 0., 0.],
#        [ 0., 1., 0., 0.],
#        [ 0., 0., 1., 0.]])
eye(3,4,1,dtype=float) # a 3x4 matrix containing zeros except for the 1st diagonal that contains ones
# array([[ 0., 1., 0., 0.],
#        [ 0., 0., 1., 0.],
#        [ 0., 0., 0., 1.]])

