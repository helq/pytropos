s = slice(3,9,2) # slice objects exist outside numpy
from numpy import *
a = arange(20)
a[s]
# array([3, 5, 7])
a[3:9:2] # same thing
# array([3, 5, 7])

