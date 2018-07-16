from numpy import *
x = array([[1,2],[3,4]])
y = array([[5,6],[7,8]])
concatenate((x,y)) # default is axis=0
# array([[1, 2],
#        [3, 4],
#        [5, 6],
#        [7, 8]])
concatenate((x,y),axis=1)
# array([[1, 2, 5, 6],
#        [3, 4, 7, 8]])

