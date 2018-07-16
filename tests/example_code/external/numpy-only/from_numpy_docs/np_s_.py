from numpy import *
s_[1:5] # easy slice generating. See r_[] examples.
# slice(1, 5, None)
s_[1:10:4]
# slice(1, 10, 4)
s_[1:10:4j]
# slice(1, 10, 4j)
s_['r',1:3] # to return a matrix. If 1-d, result is a 1xN matrix
# ('r', slice(1, 3, None))
s_['c',1:3] # to return a matrix. If 1-d, result is a Nx1 matrix
# ('c', slice(1, 3, None))

