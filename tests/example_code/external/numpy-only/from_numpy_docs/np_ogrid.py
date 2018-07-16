from numpy import *
x,y = ogrid[0:3,0:3] # x and y are useful to use with broadcasting rules
x
# array([[0],
#        [1],
#        [2]])
y
# array([[0, 1, 2]])
print((x*y)) # example how to use broadcasting rules
# [[0 0 0]
#  [0 1 2]
#  [0 2 4]]

