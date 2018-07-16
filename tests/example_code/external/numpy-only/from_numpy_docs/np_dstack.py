from numpy import *
a = array([[1,2],[3,4]]) # shapes of a and b can only differ in the 3rd dimension (if present)
b = array([[5,6],[7,8]])
dstack((a,b)) # stack arrays along a third axis (depth wise)
# array([[[1, 5],
#         [2, 6]],
#        [[3, 7],
#         [4, 8]]])

