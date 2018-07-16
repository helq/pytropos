from numpy import *
serialnr = array([1023, 5202, 6230, 1671, 1682, 5241])
height = array([40., 42., 60., 60., 98., 40.])
width = array([50., 20., 70., 60., 15., 30.])

# We want to sort the serial numbers with increasing height, _AND_
# serial numbers with equal heights should be sorted with increasing width.

indices = lexsort(keys = (width, height)) # mind the order!
indices
# array([5, 0, 1, 3, 2, 4])
for n in indices:
    print((serialnr[n], height[n], width[n]))
# ...
# 5241 40.0 30.0
# 1023 40.0 50.0
# 5202 42.0 20.0
# 1671 60.0 60.0
# 6230 60.0 70.0
# 1682 98.0 15.0

a = vstack([serialnr,width,height]) # Alternatively: all data in one big matrix
print(a) # Mind the order of the rows!
# [[ 1023. 5202. 6230. 1671. 1682. 5241.]
#  [ 50. 20. 70. 60. 15. 30.]
#  [ 40. 42. 60. 60. 98. 40.]]
indices = lexsort(a) # Sort on last row, then on 2nd last row, etc.
a.take(indices, axis=-1)
# array([[ 5241., 1023., 5202., 1671., 6230., 1682.],
#        [ 30., 50., 20., 60., 70., 15.],
#        [ 40., 40., 42., 60., 60., 98.]])

