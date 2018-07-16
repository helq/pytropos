from numpy import *
a = array([[1,2],[3,4]])
b = array([5,6])
c = broadcast(a,b)
c.nd # the number of dimensions in the broadcasted result
# 2
c.shape # the shape of the broadcasted result
# (2, 2)
c.size # total size of the broadcasted result
# 4
for value in c: print(value)
# ...
# (1, 5)
# (2, 6)
# (3, 5)
# (4, 6)
c.reset() # reset the iterator to the beginning
next(c) # next element
# (1, 5)

