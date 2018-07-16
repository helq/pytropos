from numpy import *
a = arange(4, dtype=int)
a
# array([0, 1, 2, 3])
a.fill(7) # replace all elements with the number 7
a
# array([7, 7, 7, 7])
a.fill(6.5) # fill value is converted to dtype of a
a
# array([6, 6, 6, 6])

