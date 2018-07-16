from numpy import *
x = array([1,2,3,5])
N=3
vander(x,N) # Vandermonde matrix of the vector x
# array([[ 1, 1, 1],
#        [ 4, 2, 1],
#        [ 9, 3, 1],
#        [25, 5, 1]])
column_stack([x**(N-1-i) for i in range(N)]) # to understand what a Vandermonde matrix contains
# array([[ 1, 1, 1],
#        [ 4, 2, 1],
#        [ 9, 3, 1],
#        [25, 5, 1]])

