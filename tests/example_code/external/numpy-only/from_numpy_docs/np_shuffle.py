from numpy import *
from numpy.random import shuffle
x = array([1,50,-1,3])
shuffle(x) # shuffle the elements of x
print(x)
# [-1 3 50 1]
x = ['a','b','c','z']
shuffle(x) # works with any sequence
print(x)
# ['a', 'c', 'z', 'b']

