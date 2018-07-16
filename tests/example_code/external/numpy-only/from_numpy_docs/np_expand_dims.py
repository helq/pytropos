from numpy import *
x = array([1,2])
expand_dims(x,axis=0) # Equivalent to x[newaxis,:] or x[None] or x[newaxis]
# array([[1, 2]])
expand_dims(x,axis=1) # Equivalent to x[:,newaxis]
# array([[1],
#        [2]])

