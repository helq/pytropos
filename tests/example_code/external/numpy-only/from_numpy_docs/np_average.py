from numpy import *
a = array([1,2,3,4,5])
w = array([0.1, 0.2, 0.5, 0.2, 0.2]) # weights, not necessarily normalized
average(a) # plain mean value
# 3.0
average(a,weights=w) # weighted average
# 3.1666666666666665
average(a,weights=w,returned=True) # output = weighted average, sum of weights
# (3.1666666666666665, 1.2)

