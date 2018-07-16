from numpy import *
x = array([1,2,3])
y = x.astype(float64) # convert from int32 to float64
type(y[0])
# <type 'numpy.float64'>
x.astype(None) # None implies converting to the default (float64)
# array([1., 2., 3.])

