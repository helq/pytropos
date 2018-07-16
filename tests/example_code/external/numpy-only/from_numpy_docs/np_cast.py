from numpy import *
x = arange(3)
x.dtype
# dtype('int32')
cast['int64'](x)
# array([0, 1, 2], dtype=int64)
cast['uint'](x)
# array([0, 1, 2], dtype=uint32)
cast[float128](x)
# array([0.0, 1.0, 2.0], dtype=float128)
list(cast.keys()) # list dtype cast possibilities
# <snip>

