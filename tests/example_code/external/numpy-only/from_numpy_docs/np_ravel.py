from numpy import *
a = array([[1,2],[3,4]])
a.ravel() # 1-d version of a
# array([1, 2, 3, 4])
b = a[:,0].ravel() # a[:,0] does not occupy a single memory segment, thus b is a copy, not a reference
b
# array([1, 3])
c = a[0,:].ravel() # a[0,:] occupies a single memory segment, thus c is a reference, not a copy
c
# array([1, 2])
b[0] = -1
c[1] = -2
a
# array([[ 1, -2],
#        [ 3, 4]])
ravel(a) # also exists

