from numpy import *
a = mat('1 2; 3 4')
b = mat('5 6; 7 8')
bmat('a b; b a') # all elements must be existing symbols
# matrix([[1, 2, 5, 6],
#        [3, 4, 7, 8],
#        [5, 6, 1, 2],
#        [7, 8, 3, 4]])

