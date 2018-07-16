from numpy import *
x = array([1,0,2,-1,0,0,8])
indices = x.nonzero() # find the indices of the nonzero elements
indices
# (array([0, 2, 3, 6]),)
x[indices]
# array([1, 2, -1, 8])
y = array([[0,1,0],[2,0,3]])
indices = y.nonzero()
indices
# (array([0, 1, 1]), array([1, 0, 2]))
y[indices[0],indices[1]] # one way of doing it, explains what's in indices[0] and indices[1]
# array([1, 2, 3])
y[indices] # this way is shorter
# array([1, 2, 3])
y = array([1,3,5,7])
indices = (y >= 5).nonzero()
y[indices]
# array([5, 7])
nonzero(y) # function also exists
# (array([0, 1, 2, 3]),)

