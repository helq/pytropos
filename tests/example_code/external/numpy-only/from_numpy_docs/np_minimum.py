from numpy import *
a = array([1,0,5])
b = array([3,2,4])
minimum(a,b) # element-by-element comparison
# array([1, 0, 4])
min(a.tolist(),b.tolist()) # Standard Python function does not give the same!
# [1, 0, 5]

